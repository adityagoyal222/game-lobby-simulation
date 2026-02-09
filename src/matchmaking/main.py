# CLI entrypoint
from __future__ import annotations

import argparse
from pathlib import Path

from .db import build_update_sql
from .matcher import MatchConfig, Matchmaker
from .models import PlayerEvent
from .stream import load_user_db, mock_stream_from_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mock matchmaking pipeline")
    parser.add_argument("--csv", type=Path, default=Path("synthetic_matchmaking_data.csv"))
    parser.add_argument("--mmr-threshold", type=int, default=200)
    parser.add_argument("--same-region-only", action="store_true")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--table", type=str, default="users")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = load_user_db(args.csv)

    config = MatchConfig(
        mmr_threshold=args.mmr_threshold,
        seed=args.seed,
        same_region_only=args.same_region_only,
    )
    matchmaker = Matchmaker(config)

    for payload in mock_stream_from_csv(rows, shuffle=True, seed=args.seed):
        event = PlayerEvent.from_dict(payload)
        result = matchmaker.process_event(event)
        if result is None:
            continue

        sql = build_update_sql(result, table=args.table)
        print("MATCH")
        print(f"  A: {result.player_a.user_id} (mmr {result.player_a.mmr})")
        print(f"  B: {result.player_b.user_id} (mmr {result.player_b.mmr})")
        print(f"  Winner: {result.winner_id} -> {result.winner_new_mmr}")
        print(f"  Loser:  {result.loser_id} -> {result.loser_new_mmr}")
        print("SQL")
        print(sql)
        print("-")


if __name__ == "__main__":
    main()
