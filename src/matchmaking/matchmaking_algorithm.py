"""
Matchmaking Algorithm
Handles user matchmaking logic
"""
import logging
from typing import List, Dict
from src.models.user_model import UserModel
from src.clients import database
from src.models.user_model import user_from_dict
import random
import threading

logger = logging.getLogger(__name__)


class MatchmakingAlgorithm:
    """Simple matchmaking algorithm that groups players by MMR.
    """

    def __init__(self, mmr_threshold: int | Dict[str, int] = 150):
        self.queues: Dict[str, List[UserModel]] = {}
        self.lock = threading.Lock()
        self.mmr_threshold = mmr_threshold

    def _set_ingame(self, session, user_id: str, ingame: bool):
        user = session.query(UserModel).filter_by(user_id=user_id).first()
        try:
            if not user:
                logger.warning("_set_ingame: user not found in DB", extra={"user_id": user_id})
                return None
            user.ingame = ingame
            session.add(user)
            session.commit()
            logger.debug("Set ingame status", extra={"user_id": user_id, "ingame": ingame})
            return user
        except Exception as e:
            logger.exception("Failed to set ingame status", exc_info=e, extra={"user_id": user_id})
            try:
                session.rollback()
            except Exception:
                pass
            return None

    def _update_after_game(self, session, user_id: str, new_mmr: int):
        user = session.query(UserModel).filter_by(user_id=user_id).first()
        try:
            if not user:
                logger.warning("_update_after_game: user not found in DB", extra={"user_id": user_id})
                return None
            old_mmr = user.mmr
            user.mmr = new_mmr
            user.games_played = (user.games_played or 0) + 1
            user.ingame = False
            session.add(user)
            session.commit()
            logger.info("Updated user after game", extra={"user_id": user_id, "old_mmr": old_mmr, "new_mmr": new_mmr})
            return user
        except Exception as e:
            logger.exception("Failed to update user after game", exc_info=e, extra={"user_id": user_id, "new_mmr": new_mmr})
            try:
                session.rollback()
            except Exception:
                pass
            return None

    def _find_match(self, queue: List[UserModel], mmr: int, region: str):
        """Find best candidate within the MMR threshold for the given region.

        Returns the candidate `UserModel` or `None` if no candidate within threshold.
        """
        # Determine threshold for region
        if isinstance(self.mmr_threshold, dict):
            threshold = self.mmr_threshold.get(region, max(self.mmr_threshold.values()) if self.mmr_threshold else 150)
        else:
            threshold = int(self.mmr_threshold)

        best = None
        best_diff = None
        for candidate in queue:
            diff = abs(candidate.mmr - mmr)
            if diff <= threshold:
                if best is None or diff < best_diff:
                    best = candidate
                    best_diff = diff
        return best

    def get_user(self, user_data: Dict) -> None:
        logger.info("Processing user for matchmaking", extra={"user_id": user_data.get('user_id')})

        session = None
        try:
            session = database.get_session()
            if session is None:
                logger.error("No DB session available; skipping user", extra={"user_id": user_data.get('user_id')})
                return

            # Mark user as ingame=True 
            db_user = session.query(UserModel).filter_by(user_id=user_data.get('user_id')).first()
            if not db_user:
                db_user = UserModel(**user_data)
                session.add(db_user)
                session.commit()

            # If already in a game, skip
            if db_user.ingame:
                logger.info("User already ingame; skipping", extra={"user_id": db_user.user_id})
                return

            self._set_ingame(session, db_user.user_id, True)

            incoming = user_from_dict(user_data)

            region = incoming.region or "global"

            with self.lock:
                q = self.queues.setdefault(region, [])

                # Try to find match (uses region-specific threshold if provided)
                match = self._find_match(q, incoming.mmr, region)

                if not match:
                    # No suitable match -> enqueue
                    q.append(incoming)
                    logger.info("Enqueued user", extra={"user_id": incoming.user_id, "mmr": incoming.mmr, "region": region, "queue_size": len(q)})
                    return

                q.remove(match)

            # Resolve match outside lock 
            players = (incoming, match)
            try:
                winner = random.choice(players)
                loser = match if winner is incoming else incoming

                winner_new = max(0, winner.mmr + 25)
                loser_new = max(0, loser.mmr - 25)

                self._update_after_game(session, winner.user_id, winner_new)
                self._update_after_game(session, loser.user_id, loser_new)

                logger.info("Match resolved", extra={"player_a": incoming.user_id, "player_b": match.user_id, "winner": winner.user_id})
            except Exception as e:
                logger.exception("Error resolving match", exc_info=e, extra={"player_a": incoming.user_id, "player_b": getattr(match, 'user_id', None)})

        except Exception as e:
            logger.error(f"Error in matchmaking.get_user: {e}")
        finally:
            if session:
                try:
                    session.close()
                except Exception:
                    pass
