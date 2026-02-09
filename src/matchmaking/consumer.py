"""
Kafka Consumer for Matchmaking System
Consumes users from Kafka and sends them to matchmaking algorithm
Ultra simplified: Just read users and pass to blackbox algorithm
"""
import logging
import signal
from typing import Optional, Callable
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from src.clients.kafka_config import KafkaConfig
from src.clients.database import connect_db, init_db
from src.models.user_model import UserModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MatchmakingConsumer:
    """
    Kafka consumer that reads users and sends to matchmaking algorithm
    Simplified: Reads UserModel JSON, passes to callback (blackbox algorithm)
    """

    def __init__(
        self,
        config: Optional[KafkaConfig] = None,
        matchmaking_callback: Optional[Callable[[UserModel], None]] = None
    ):
        """
        Initialize Kafka consumer

        Args:
            config: KafkaConfig object, if None will load from environment
            matchmaking_callback: Function called for each user received.
                                 This is your blackbox matchmaking algorithm.
        """
        self.config = config or KafkaConfig.from_env()
        self.consumer: Optional[KafkaConsumer] = None
        self.matchmaking_callback = matchmaking_callback

        # Initialize database connection
        logger.info("Connecting to database...")
        if connect_db():
            init_db()
        else:
            raise RuntimeError("Failed to connect to database")

        self.is_running = False
        self.is_connected = False
        self.users_processed = 0

    def connect(self) -> bool:
        """
        Establish connection to Kafka broker

        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to Kafka at {self.config.bootstrap_servers}...")

            consumer_config = self.config.get_consumer_config()

            self.consumer = KafkaConsumer(
                self.config.topic_matchmaking,
                **consumer_config,
                value_deserializer=lambda v: v.decode('utf-8'),
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
            )

            self.is_connected = True
            logger.info(f"Kafka consumer connected successfully to topic: {self.config.topic_matchmaking}")
            return True

        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Kafka: {e}")
            self.is_connected = False
            return False

    def _process_user(self, user: UserModel) -> None:
        """
        Process a user from Kafka - send to matchmaking algorithm

        Args:
            user: UserModel to process
        """
        try:
            if self.matchmaking_callback:
                self.matchmaking_callback(user)
            self.users_processed += 1
        except Exception as e:
            logger.error(f"Error processing user: {e}", exc_info=True)

    def start(self) -> None:
        """
        Start consuming messages from Kafka
        """
        if not self.is_connected:
            logger.error("Consumer not connected. Call connect() first.")
            return

        if self.is_running:
            logger.warning("Consumer is already running")
            return

        self.is_running = True

        logger.info("Starting matchmaking consumer...")
        logger.info("Waiting for users... (Press Ctrl+C to stop)")

        try:
            for message in self.consumer:
                if not self.is_running:
                    break

                try:
                    # Deserialize user from JSON
                    user = UserModel.from_json(message.value)

                    logger.info(
                        f"Received user {user.user_id} "
                        f"(MMR: {user.mmr}, Region: {user.region})"
                    )

                    # Send to matchmaking algorithm
                    self._process_user(user)

                    # Log status periodically
                    if self.users_processed % 10 == 0:
                        logger.info(f"Processed {self.users_processed} users so far")

                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    continue

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stop consuming messages and cleanup"""
        if not self.is_running:
            return

        logger.info("Stopping matchmaking consumer...")
        self.is_running = False

        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")

        logger.info(f"Total users processed: {self.users_processed}")

    def get_stats(self) -> dict:
        """
        Get consumer statistics

        Returns:
            Dictionary with consumer statistics
        """
        return {
            "users_processed": self.users_processed,
            "is_running": self.is_running,
            "is_connected": self.is_connected
        }

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


def setup_signal_handlers(consumer: MatchmakingConsumer) -> None:
    """
    Setup signal handlers for graceful shutdown

    Args:
        consumer: MatchmakingConsumer instance
    """
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}")
        consumer.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

