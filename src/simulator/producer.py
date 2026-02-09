"""
Kafka Producer for Matchmaking System
Sends users to Kafka topic - ultra simple, just stream User objects
"""
import logging
from datetime import datetime
from typing import Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from src.clients.kafka_config import KafkaConfig
from src.models.user_model import UserModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MatchmakingProducer:
    """
    Kafka producer for sending users to matchmaking queue
    Simplified: Just sends UserModel JSON to Kafka
    """
    
    def __init__(self, config: Optional[KafkaConfig] = None):
        """
        Initialize Kafka producer
        
        Args:
            config: KafkaConfig object, if None will load from environment
        """
        self.config = config or KafkaConfig.from_env()
        self.producer: Optional[KafkaProducer] = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """
        Establish connection to Kafka broker
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to Kafka at {self.config.bootstrap_servers}...")
            
            producer_config = self.config.get_producer_config()
            
            self.producer = KafkaProducer(
                **producer_config,
                value_serializer=lambda v: v.encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
            )
            
            self.is_connected = True
            logger.info("Kafka producer connected successfully")
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self.is_connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Kafka: {e}")
            self.is_connected = False
            return False
    
    def send_user(self, user: UserModel) -> bool:
        """
        Send a user to Kafka matchmaking queue

        Args:
            user: UserModel object to send
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.is_connected or not self.producer:
            logger.error("Producer not connected. Call connect() first.")
            return False
        
        try:
            # Send user JSON to Kafka with user_id as key for partitioning
            future = self.producer.send(
                self.config.topic_matchmaking,
                key=user.user_id,
                value=user.to_json()
            )
            
            # Wait for confirmation (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Sent {user.user_id} to Kafka "
                f"(partition: {record_metadata.partition}, offset: {record_metadata.offset})"
            )
            
            return True
            
        except KafkaError as e:
            logger.error(f"Kafka error sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False
    
    def flush(self, timeout: Optional[float] = None) -> None:
        """
        Flush any pending messages
        
        Args:
            timeout: Maximum time to wait for flush (seconds)
        """
        if self.producer:
            self.producer.flush(timeout=timeout)
            logger.info("Flushed pending messages")
    
    def close(self) -> None:
        """Close the producer and cleanup resources"""
        if self.producer:
            logger.info("Closing Kafka producer...")
            self.producer.close()
            self.is_connected = False
            logger.info("Kafka producer closed")
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

