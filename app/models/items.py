from sqlalchemy import Column, String, Float, Boolean, Integer
from sqlalchemy.orm import sessionmaker

from app.database.db import Base, engine


class Item(Base):
    __tablename__ = "Items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    availability_status = Column(String)
    manufacturer = Column(String)
    quantity = Column(Integer)
