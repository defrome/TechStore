import uuid

from pydantic import UUID1
from sqlalchemy import create_engine, Float, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String


SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})


class Base(DeclarativeBase): pass


class User(Base):
    __tablename__ = "Users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    first_name = Column(String)
    surname = Column(String)
    status = Column(String)
    balance = Column(Float)
    is_premium = Column(Boolean)
    number_of_orders = Column(Integer)


SessionLocal = sessionmaker(autoflush=False, bind=engine)