# SQL update string generator

from __future__ import annotations

from .models import MatchResult


def build_update_sql(result: MatchResult, table: str = "users") -> str:
    statements = [
        "BEGIN;",
        f"UPDATE {table} SET mmr = {result.winner_new_mmr} WHERE user_id = '{result.winner_id}';",
        f"UPDATE {table} SET mmr = {result.loser_new_mmr} WHERE user_id = '{result.loser_id}';",
        "COMMIT;",
    ]
    return "\n".join(statements)
