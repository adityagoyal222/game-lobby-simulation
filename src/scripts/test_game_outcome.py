from sqlalchemy import func
from src.clients.database import connect_db, init_db, get_session
from src.models.user_model import UserModel
from src.game_outcome.game_outcome import GameOutcomeService


def main():
    if not connect_db():
        raise RuntimeError("DB connection failed. Check .env values.")

    init_db()
    session = get_session()

    users = session.query(UserModel).order_by(func.random()).limit(2).all()
    if len(users) < 2:
        raise RuntimeError("Not enough users in DB. Run datagen.py first.")

    a, b = users[0], users[1]

    # simulate that matchmaking sets ingame=True before game starts
    a.ingame = True
    b.ingame = True
    session.add(a)
    session.add(b)
    session.commit()

    service = GameOutcomeService()
    outcome = service.run_match(a.user_id, b.user_id, delay_seconds=1)  # quick test
    print("\nOUTCOME:\n", outcome)

    session.expire_all()

    # verify DB changes
    a2 = session.query(UserModel).filter_by(user_id=a.user_id).first()
    b2 = session.query(UserModel).filter_by(user_id=b.user_id).first()
    print("\nPOST DB CHECK:")
    print("A:", a2.user_id, "MMR:", a2.mmr, "ingame:", a2.ingame, "games:", a2.games_played)
    print("B:", b2.user_id, "MMR:", b2.mmr, "ingame:", b2.ingame, "games:", b2.games_played)

    session.close()


if __name__ == "__main__":
    main()
