"""
Game Outcome Module (Sharmeen)

Responsibilities:
- Receive two user_ids from matchmaking
- Simulate fight (delay)
- Decide winner/loser (fighting-game style probability)
- Update ONLY users table:
    - winner/loser MMR
    - games_played + 1 for both
    - ingame = False for both
"""

from __future__ import annotations

import time
import random
import logging
from dataclasses import dataclass
from typing import Tuple

from src.clients import database
from src.models.user_model import UserModel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MatchOutcome:
    player_a_id: str
    player_b_id: str
    winner_id: str
    loser_id: str
    winner_old_mmr: int
    loser_old_mmr: int
    winner_new_mmr: int
    loser_new_mmr: int
    finish_type: str


class GameOutcomeService:
    def __init__(self, mmr_win: int = 25, mmr_loss: int = 25):
        self.mmr_win = mmr_win
        self.mmr_loss = mmr_loss

    def _pick_winner(self, a: UserModel, b: UserModel) -> Tuple[UserModel, UserModel, str]:
        """
        Higher MMR gives slightly higher chance to win.
        But still random (so upsets can happen).
        """
        diff = (a.mmr or 0) - (b.mmr or 0)
        advantage = max(-0.15, min(0.15, diff / 2000))  # clamp +/-15%
        p_a = 0.5 + advantage

        finish_type = "KO" if random.random() < 0.35 else "DECISION"

        if random.random() < p_a:
            return a, b, finish_type
        return b, a, finish_type

    def _compute_new_mmr(self, winner_mmr: int, loser_mmr: int) -> Tuple[int, int]:
        winner_new = max(0, min(5000, winner_mmr + self.mmr_win))
        loser_new = max(0, min(5000, loser_mmr - self.mmr_loss))
        return winner_new, loser_new

    def run_match(self, user_a_id: str, user_b_id: str, delay_seconds: int = 10) -> MatchOutcome:
        """
        Called by matchmaking when a pair is found.
        Updates DB and returns outcome.
        """
        if not database.connect_db():
            raise RuntimeError("Database not connected. Check your .env values.")

        session = database.get_session()
        try:
            a = session.query(UserModel).filter_by(user_id=user_a_id).first()
            b = session.query(UserModel).filter_by(user_id=user_b_id).first()

            if not a or not b:
                raise ValueError("One or both users not found in DB.")

            logger.info(f"[OUTCOME] Match starting: {a.user_id} vs {b.user_id}")

            # Simulate match time
            time.sleep(delay_seconds)

            # Decide winner
            winner, loser, finish_type = self._pick_winner(a, b)

            winner_old = int(winner.mmr)
            loser_old = int(loser.mmr)

            winner_new, loser_new = self._compute_new_mmr(winner_old, loser_old)

            # Update users table
            winner.mmr = winner_new
            loser.mmr = loser_new

            winner.games_played = (winner.games_played or 0) + 1
            loser.games_played = (loser.games_played or 0) + 1

            winner.ingame = False
            loser.ingame = False

            session.add(winner)
            session.add(loser)
            session.commit()

            outcome = MatchOutcome(
                player_a_id=a.user_id,
                player_b_id=b.user_id,
                winner_id=winner.user_id,
                loser_id=loser.user_id,
                winner_old_mmr=winner_old,
                loser_old_mmr=loser_old,
                winner_new_mmr=winner_new,
                loser_new_mmr=loser_new,
                finish_type=finish_type,
            )

            logger.info(
                f"[OUTCOME] Winner={outcome.winner_id} ({outcome.winner_old_mmr}->{outcome.winner_new_mmr}) | "
                f"Loser={outcome.loser_id} ({outcome.loser_old_mmr}->{outcome.loser_new_mmr}) | "
                f"Finish={outcome.finish_type}"
            )

            return outcome

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
