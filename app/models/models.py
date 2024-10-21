from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
from app.utils.database import Base
import datetime
from pydantic import ConfigDict

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    games = relationship("Game", back_populates="user")

    model_config = ConfigDict(from_attributes=True)

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    theme = Column(String)
    difficulty = Column(Integer)
    score = Column(Integer, default=0)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime)
    user = relationship("User", back_populates="games")
    puzzles = relationship("Puzzle", back_populates="game")

    model_config = ConfigDict(from_attributes=True)

class Puzzle(Base):
    __tablename__ = "puzzles"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    question = Column(String)
    answer = Column(String)
    hints = Column(String)
    difficulty = Column(Float, default=1.0)
    attempts = Column(Integer, default=0)
    time_spent = Column(Float, default=0.0)
    solved = Column(Boolean, default=False)
    game = relationship("Game", back_populates="puzzles")

    model_config = ConfigDict(from_attributes=True)