import uuid

from sqlalchemy import Column, String, Float, Boolean, Integer
from sqlalchemy.orm import sessionmaker

from app.database.db import Base, engine


class User(Base):
    __tablename__ = "Users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    first_name = Column(String)
    surname = Column(String)
    status = Column(String)
    balance = Column(Float)
    is_premium = Column(Boolean)
    number_of_orders = Column(Integer)
    hashed_password = Column(String)


SessionLocal = sessionmaker(autoflush=False, bind=engine)