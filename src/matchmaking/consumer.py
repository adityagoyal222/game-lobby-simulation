"""
Matchmaking Consumer using Google Pub/Sub
"""
import logging
import json
import signal
import sys
from concurrent import futures
from google.cloud import pubsub_v1
from src.clients.pubsub_config import PubSubConfig
from src.matchmaking.matchmaking_algorithm import MatchmakingAlgorithm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MatchmakingConsumer:
    def __init__(self, config: PubSubConfig = None):
        self.config = config or PubSubConfig.from_env()
        self.subscriber = None
        self.subscription_path = None
        self.matchmaker = MatchmakingAlgorithm()
        self.is_running = False
        self.messages_processed = 0

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def _callback(self, message: pubsub_v1.subscriber.message.Message):
        try:
            user_data = json.loads(message.data.decode("utf-8"))
            logger.info(f"Received user: {user_data.get('user_id')}")

            self.matchmaker.get_user(user_data)
            
            message.ack()
            self.messages_processed += 1

            if self.messages_processed % 10 == 0:
                logger.info(f"Processed {self.messages_processed} messages")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            message.nack()

    def start(self):
        logger.info("Starting Pub/Sub consumer...")
        try:
            self.subscriber = pubsub_v1.SubscriberClient()
            self.subscription_path = self.subscriber.subscription_path(
                self.config.project_id, self.config.subscription_id
            )

            self.is_running = True
            logger.info(f"Listening on subscription: {self.config.subscription_id}")

            streaming_pull_future = self.subscriber.subscribe(
                self.subscription_path, callback=self._callback
            )

            with futures.ThreadPoolExecutor(max_workers=10) as executor:
                try:
                    streaming_pull_future.result()
                except Exception as e:
                    logger.error(f"Streaming pull error: {e}")
                    streaming_pull_future.cancel()
                    streaming_pull_future.result()

        except Exception as e:
            logger.error(f"Failed to start consumer: {e}")
        finally:
            self.stop()

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        logger.info(f"Stopping (processed {self.messages_processed} messages)")
        if self.subscriber:
            self.subscriber.close()


if __name__ == "__main__":
    consumer = MatchmakingConsumer()
    consumer.start()
