"""
User Model - Single unified model for both ORM and data transfer
Combines SQLAlchemy database model with JSON serialization for Kafka
"""
import json
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Index
from datetime import datetime
from src.clients.database import Base


class Region(str, Enum):
    """Available game regions"""
    America = "America"
    Europe = "Europe"
    Asia = "Asia"
    Africa = "Africa"
    Oceania = "Oceania"

    # Backward compatibility aliases
    NA = "America"
    EU = "Europe"
    ASIA = "Asia"
    SA = "Africa"
    OCE = "Oceania"


class UserModel(Base):
    """Database model for users - also used as data transfer object"""
    __tablename__ = 'users'
    
    user_id = Column(String(255), primary_key=True)
    mmr = Column(Integer, index=True, nullable=False)
    region = Column(String(50), index=True, nullable=False)
    games_played = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    ingame = Column(Boolean, default=False, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    __table_args__ = (
        Index('idx_mmr', 'mmr'),
        Index('idx_region', 'region'),
        Index('idx_ingame', 'ingame'),
    )

    def to_json(self) -> str:
        """Serialize user to JSON string for Kafka"""
        data = {
            "user_id": self.user_id,
            "mmr": self.mmr,
            "region": self.region if isinstance(self.region, str) else self.region.value,
            "games_played": self.games_played,
            "level": self.level,
            "ingame": self.ingame
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> "UserModel":
        """
        Create a UserModel instance from JSON string (for Kafka messages)
        This creates a temporary object - NOT saved to database
        """
        data = json.loads(json_str)

        # Handle region conversion
        if isinstance(data.get("region"), str):
            try:
                data["region"] = Region(data["region"]).value
            except ValueError:
                pass  # Keep as string if not valid enum

        # Create instance without saving to database
        return cls(**data)

    def __repr__(self) -> str:
        """String representation for logging"""
        return f"User[{self.user_id}, MMR={self.mmr}, Region={self.region}]"


# Convenience function to create user from dict (used by queue_manager)
def user_from_dict(data: dict) -> UserModel:
    """
    Create a UserModel instance from a dictionary
    Useful when converting from database results
    """
    user = UserModel()
    user.user_id = data.get("user_id")
    user.mmr = data.get("mmr")
    user.region = data.get("region")
    user.games_played = data.get("games_played", 0)
    user.level = data.get("level", 1)
    user.ingame = data.get("ingame", False)
    return user
