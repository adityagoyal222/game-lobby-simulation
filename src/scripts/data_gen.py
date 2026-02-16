"""
Synthetic Data Generator for Matchmaking System
Generates realistic user data and writes directly to PostgreSQL database

Usage: python -m src.scripts.data_gen
"""
import uuid
import random
import sys
from sqlalchemy import func
from src.clients.database import connect_db, init_db, get_session
from src.models.user_model import UserModel, Region
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Number of synthetic players
NUM_PLAYERS = 2000

# Possible regions with intentionally uneven distribution
regions = [Region.America, Region.Europe, Region.Asia, Region.Africa, Region.Oceania]
region_weights = [0.35, 0.30, 0.20, 0.10, 0.05]  # Realistic distribution


def generate_player() -> dict:
    """Generate a single synthetic player with realistic stats"""
    user_id = str(uuid.uuid4())

    # MMR distribution based on League of Legends ranking system
    mmr_mean = 2000  # Average player
    mmr_std = 600    # Standard deviation
    mmr = int(random.gauss(mmr_mean, mmr_std))
    mmr = max(0, min(5000, mmr))  # Clamp between 0-5000

    # Games played correlates with MMR
    games_played = int(random.gauss(mmr / 10, 20))
    games_played = max(0, games_played)

    # Region with weighted randomness
    region = random.choices(regions, weights=region_weights, k=1)[0]

    # Level: correlated with games played
    level = max(1, int(games_played / 15 + random.randint(-3, 5)))

    return {
        "user_id": user_id,
        "mmr": mmr,
        "games_played": games_played,
        "region": region.value,
        "level": level,
        "ingame": False
    }


def populate_database(num_players: int = NUM_PLAYERS, batch_size: int = 100):
    """
    Generate synthetic players and insert them into the database

    Args:
        num_players: Number of players to generate
        batch_size: Number of records to insert at once
    """
    inserted = 0
    batch = []
    session = get_session()

    for i in range(num_players):
        player = generate_player()
        batch.append(UserModel(**player))

        # Insert batch when it reaches batch_size or at the end
        if len(batch) >= batch_size or i == num_players - 1:
            try:
                # Bulk insert
                session.bulk_save_objects(batch)
                session.commit()
                inserted += len(batch)
                batch = []
            except Exception as e:
                print(f"Error inserting batch: {e}")
                session.rollback()
                batch = []

    print(f"Data generated successfully: {inserted} players inserted")

    session.close()

    return True


def clear_database():
    """Clear all users from the database"""
    session = get_session()
    try:
        count = session.query(UserModel).delete()
        session.commit()
        print(f"Deleted {count} users from database")
    except Exception as e:
        print(f"Could not clear database (table may not exist yet): {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic matchmaking data")
    parser.add_argument(
        "--players",
        type=int,
        default=NUM_PLAYERS,
        help=f"Number of players to generate (default: {NUM_PLAYERS})"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all existing users before generating new ones"
    )
    parser.add_argument(
        "--clear-only",
        action="store_true",
        help="Only clear the database, don't generate new data"
    )

    args = parser.parse_args()

    # Connect to database first
    if not connect_db():
        print("Failed to connect to database. Check your .env configuration.")
        sys.exit(1)
    
    print("Database initialized")

    # Clear database if requested (tables already created by init_db.py)
    if args.clear or args.clear_only:
        clear_database()

        if args.clear_only:
            sys.exit(0)

    # Generate and populate database
    success = populate_database(num_players=args.players)

    if not success:
        sys.exit(1)
