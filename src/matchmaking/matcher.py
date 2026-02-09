# matchmaking logic and config
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .models import PlayerEvent, MatchResult


@dataclass
class MatchConfig:
    mmr_threshold: int = 200
    mmr_delta_win: int = 25
    mmr_delta_loss: int = -25
    seed: Optional[int] = None
    same_region_only: bool = True


@dataclass
class Matchmaker:
    config: MatchConfig
    waiting_by_region: Dict[str, List[PlayerEvent]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.config.seed is not None:
            random.seed(self.config.seed)

    def process_event(self, event: PlayerEvent) -> Optional[MatchResult]:
        if event.ingame:
            return None

        region_key = event.region if self.config.same_region_only else "*"
        pool = self.waiting_by_region.setdefault(region_key, [])

        match_index = self._find_best_match_index(pool, event)
        if match_index is None:
            pool.append(event)
            return None

        opponent = pool.pop(match_index)
        return self._resolve_match(event, opponent)

    def _find_best_match_index(self, pool: List[PlayerEvent], event: PlayerEvent) -> Optional[int]:
        best_index = None
        best_diff = None
        for i, candidate in enumerate(pool):
            diff = abs(candidate.mmr - event.mmr)
            if diff <= self.config.mmr_threshold:
                if best_diff is None or diff < best_diff:
                    best_diff = diff
                    best_index = i
        return best_index

    def _resolve_match(self, a: PlayerEvent, b: PlayerEvent) -> MatchResult:
        winner, loser = (a, b) if random.random() < 0.5 else (b, a)
        winner_new = winner.mmr + self.config.mmr_delta_win
        loser_new = max(0, loser.mmr + self.config.mmr_delta_loss)
        return MatchResult(
            player_a=a,
            player_b=b,
            winner_id=winner.user_id,
            loser_id=loser.user_id,
            winner_new_mmr=winner_new,
            loser_new_mmr=loser_new,
        )
