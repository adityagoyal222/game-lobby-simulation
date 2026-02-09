# mock stream loader (CSV -> events) will be deleted of course
from __future__ import annotations

import csv
import random
from pathlib import Path
from typing import Dict, Iterable, Iterator, List


def load_user_db(csv_path: Path) -> List[Dict[str, str]]:
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def mock_stream_from_csv(rows: List[Dict[str, str]], shuffle: bool = True, seed: int | None = 7) -> Iterator[Dict[str, str]]:
    data = rows[:]
    if shuffle:
        if seed is not None:
            random.seed(seed)
        random.shuffle(data)
    for row in data:
        yield {
            "user_id": row["user_id"],
            "mmr": int(row["MMR"]),
            "region": row["region"],
            "games_played": int(row["games_played"]),
            "level": int(row["level"]),
            "ingame": row["ingame"].lower() == "true",
        }
