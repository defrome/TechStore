import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, Table, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base

item_category = Table(
    'item_category',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('Items.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    def __repr__(self):
        return f"Cart(item_id={self.item_id}, quantity={self.item_value})"

class Cart(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    item_id = Column(Integer, ForeignKey('Items.id', ondelete="CASCADE"))
    item_value = Column(Integer, default=1)

    item = relationship("Item", back_populates="cart_associations")

    def __repr__(self):
        return f"Cart(item_id={self.item_id}, quantity={self.item_value})"

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
    cart_associations = relationship("Cart", back_populates="item")
    order_items = relationship("OrderItem", back_populates="item")

    @property
    def in_carts(self):
        return [assoc.user for assoc in self.cart_associations]

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


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    item_id = Column(Integer, ForeignKey('Items.id'))
    quantity = Column(Integer)
    price_at_time = Column(Integer)

    order = relationship("Order", back_populates="order_items")
    item = relationship("Item", back_populates="order_items")

    def __repr__(self):
        return f"OrderItem(order_id={self.order_id}, item_id={self.item_id}, quantity={self.quantity})"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Integer, default=0)
    total_items = Column(Integer, default=0)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Order(id={self.id}, status='{self.status}')"