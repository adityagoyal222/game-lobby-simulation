"""
Matchmaking Algorithm
Handles user matchmaking logic
"""
import logging
from typing import List, Dict
from src.models.user_model import UserModel

logger = logging.getLogger(__name__)


class MatchmakingAlgorithm:
    """Simple matchmaking algorithm that groups players by MMR"""

    def get_user(self, user_data: Dict) -> None:
        print(f"Processing user for matchmaking: {user_data}")
