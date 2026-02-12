"""
Google Pub/Sub Configuration for Matchmaking System
"""
import os
from dotenv import load_dotenv

load_dotenv()


class PubSubConfig:
    """Configuration for Google Pub/Sub"""

    def __init__(self):
        self.project_id = os.getenv("GCP_PROJECT_ID", "game-lobby-simulation")
        self.topic_id = os.getenv("PUBSUB_TOPIC_ID", "matchmaking-queue")
        self.subscription_id = os.getenv("PUBSUB_SUBSCRIPTION_ID", "matchmaking-subscription")

    @classmethod
    def from_env(cls):
        return cls()
