import uuid
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database.db import Base

item_category = Table(
    'item_category',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('Items.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)


class Cart(Base):
    __tablename__ = 'cart_items'

    user_id = Column(String(36), ForeignKey('Users.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('Items.id'), primary_key=True)
    item_value = Column(Integer, default=1)

    # Relationships для доступа к связанным объектам
    user = relationship("User", back_populates="cart_associations")
    item = relationship("Item", back_populates="cart_associations")


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

    # Relationships через модель Cart
    cart_associations = relationship("Cart", back_populates="user")

    # Для прямого доступа к товарам в корзине
    @property
    def cart_items(self):
        return [assoc.item for assoc in self.cart_associations]

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
    cart_associations = relationship("Cart", back_populates="item")

    # Для прямого доступа к пользователям, у которых товар в корзине
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