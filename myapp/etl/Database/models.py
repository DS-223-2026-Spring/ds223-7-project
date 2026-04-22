from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    plan = Column(String)
    segment = Column(String)
    created_at = Column(DateTime)
