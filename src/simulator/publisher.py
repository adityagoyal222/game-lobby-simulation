"""
Google Pub/Sub Publisher for Matchmaking System
"""
import logging
from typing import Optional
from google.cloud import pubsub_v1
from src.clients.pubsub_config import PubSubConfig
from src.models.user_model import UserModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MatchmakingPublisher:
    def __init__(self, config: Optional[PubSubConfig] = None):
        self.config = config or PubSubConfig.from_env()
        self.publisher: Optional[pubsub_v1.PublisherClient] = None
        self.topic_path: Optional[str] = None
        self.is_connected = False

    def connect(self) -> bool:
        try:
            self.publisher = pubsub_v1.PublisherClient()
            self.topic_path = self.publisher.topic_path(
                self.config.project_id, self.config.topic_id
            )
            self.is_connected = True
            logger.info(f"Pub/Sub publisher connected to topic: {self.config.topic_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect publisher: {e}")
            return False

    def publish_user(self, user: UserModel) -> bool:
        if not self.is_connected or not self.publisher:
            logger.error("Publisher not connected")
            return False
        try:
            data = user.to_json().encode("utf-8")
            future = self.publisher.publish(self.topic_path, data, user_id=str(user.user_id))
            future.result()  # Wait for publish to complete
            return True
        except Exception as e:
            logger.error(f"Failed to publish user {user.user_id}: {e}")
            return False

    def close(self):
        if self.publisher:
            logger.info("Closing Pub/Sub publisher")
            self.is_connected = False
