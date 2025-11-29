import uuid
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, relationship
from app.database.db import Base, engine

item_category = Table(
    'item_category',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('Items.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

cart_items = Table(
    'cart_items',
    Base.metadata,
    Column('cart_id', Integer, ForeignKey('carts.id')),
    Column('item_id', Integer, ForeignKey('Items.id'))
)


class User(Base):
    __tablename__ = "Users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    first_name = Column(String)
    surname = Column(String)
    status = Column(String)
    balance = Column(Float)
    is_premium = Column(Boolean)
    number_of_orders = Column(Integer)
    avatar_image = Column(String)

    cart = relationship("Cart", back_populates="user", uselist=False)

    def __repr__(self):
        return f"User(id={self.id}, first_name='{self.first_name}', surname='{self.surname}')"


class Item(Base):
    __tablename__ = "Items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    availability_status = Column(Boolean)
    manufacturer = Column(String)
    quantity = Column(Integer)
    image = Column(String)

    categories = relationship("Category", secondary=item_category, back_populates="items")
    carts = relationship("Cart", secondary=cart_items, back_populates="items")

    def __repr__(self):
        return f"Item(id={self.id}, name='{self.name}')"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    items = relationship("Item", secondary=item_category, back_populates="categories")

    def __repr__(self):
        return f"Category(id={self.id}, name='{self.name}')"


class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey('Users.id'))

    # Relationships
    user = relationship("User", back_populates="cart")
    items = relationship("Item", secondary=cart_items, back_populates="carts")

    def __repr__(self):
        return f"Cart(id={self.id}, user_id='{self.user_id}')"