"""
User Model - Single unified model for both ORM and data transfer
Combines Peewee database model with JSON serialization for Kafka
"""
import json
from enum import Enum
from peewee import Model, CharField, IntegerField, BooleanField, DateTimeField
from datetime import datetime
from src.clients.database import db


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


class UserModel(Model):
    """Database model for users - also used as data transfer object"""
    user_id = CharField(primary_key=True, max_length=255)
    mmr = IntegerField(index=True)
    region = CharField(max_length=50, index=True)
    games_played = IntegerField(default=0)
    level = IntegerField(default=1)
    ingame = BooleanField(default=False, index=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'users'

    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

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
