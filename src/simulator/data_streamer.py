"""
Data Streamer for Matchmaking Simulation using Google Pub/Sub
"""
import logging
import random
import time
import signal
import sys
from typing import Optional
from sqlalchemy import func
from dotenv import load_dotenv
from src.clients.database import connect_db, get_session
from src.models.user_model import UserModel
from src.simulator.publisher import MatchmakingPublisher

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DataStreamer:
    def __init__(self, min_interval=10.0, max_interval=30.0, batch_size=100):
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.batch_size = batch_size
        self.publisher: Optional[MatchmakingPublisher] = None
        self.is_running = False
        self.users_sent = 0

        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)

    def _get_random_users(self, session, count):
        try:
            total_users = session.query(func.count(UserModel.user_id)).scalar()
            if total_users == 0:
                logger.warning("No users in DB")
                return []
            users = session.query(UserModel).order_by(func.random()).limit(count).all()
            return users
        except Exception as e:
            logger.error(f"Error fetching users: {e}")
            return []

    def start(self):
        logger.info("=" * 60)
        logger.info("DATA STREAMER STARTING")
        logger.info("=" * 60)

        if not connect_db():
            logger.error("FAILED: Could not connect to database")
            return
        logger.info("SUCCESS: Database connection established")

        self.publisher = MatchmakingPublisher()
        if not self.publisher.connect():
            logger.error("FAILED: Could not connect to Pub/Sub")
            return
        logger.info("SUCCESS: Pub/Sub connection established")

        self.is_running = True
        logger.info(f"Streaming users every {self.min_interval}-{self.max_interval}s")
        logger.info("=" * 60)
        session = get_session()

        try:
            while self.is_running:
                users = self._get_random_users(session, self.batch_size)
                if not users:
                    time.sleep(5)
                    continue

                user = random.choice(users)
                if self.publisher.publish_user(user):
                    self.users_sent += 1
                    logger.info(f"Published user {user.user_id[:8]}... (MMR: {user.mmr}, Region: {user.region})")
                    if self.users_sent % 10 == 0:
                        logger.info(f">>> Total published: {self.users_sent} users <<<")

                time.sleep(random.uniform(self.min_interval, self.max_interval))

        except Exception as e:
            logger.error(f"Error in streamer: {e}")
        finally:
            session.close()
            self.stop()

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        logger.info(f"Stopping (published {self.users_sent} users)")
        if self.publisher:
            self.publisher.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-interval", type=float, default=0.1)
    parser.add_argument("--max-interval", type=float, default=2.0)
    parser.add_argument("--batch-size", type=int, default=10)
    args = parser.parse_args()

    streamer = DataStreamer(
        min_interval=args.min_interval,
        max_interval=args.max_interval,
        batch_size=args.batch_size
    )
    streamer.start()
