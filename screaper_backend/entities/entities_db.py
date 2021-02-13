"""
    Declares all database entities.
    This will likely match with front-end code
"""
import datetime

from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    # Whenever a new catalogue comes in, just append these parts! (and update the timestamp)
    __tablename__ = 'products'

    id = Column(Integer, autoincrement=True, primary_key=True)
    product_external_identifier = Column(String)
    manufacturer_status = Column(String)
    manufacturer_price = Column(Float)
    manufacturer_stock = Column(Integer)
    manufacturer = Column(String)
    manufacturer_abbreviation = Column(String)
    weight_in_g = Column(Float)
    replaced_by = Column(String)

    changes = Column(Integer)
    shortcut = Column(String)
    hs_code = Column(String)
    important = Column(String)

    description_en = Column(String)
    description_de = Column(String)

    price_currency = Column(String)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, autoincrement=True, primary_key=True)

    user_name = Column(String)
    company_name = Column(String)
    phone_number = Column(String)
    email = Column(String)
    address = Column(String)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, autoincrement=True, primary_key=True)

    # customer_id = Column(Integer, ForeignKey("users.id"))

    reference = Column(String)
    origin = Column(String)
    status = Column(String)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, autoincrement=True, primary_key=True)

    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price = Column(Float)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
