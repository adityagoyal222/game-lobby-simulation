# dataclasses for events and match results
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class PlayerEvent:
    user_id: str
    mmr: int
    region: str
    games_played: int
    level: int
    ingame: bool

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PlayerEvent":
        return PlayerEvent(
            user_id=str(data["user_id"]),
            mmr=int(data["mmr"]),
            region=str(data["region"]),
            games_played=int(data["games_played"]),
            level=int(data["level"]),
            ingame=bool(data["ingame"]),
        )


@dataclass
class MatchResult:
    player_a: PlayerEvent
    player_b: PlayerEvent
    winner_id: str
    loser_id: str
    winner_new_mmr: int
    loser_new_mmr: int
