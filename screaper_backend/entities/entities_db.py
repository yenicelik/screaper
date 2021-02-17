"""
    Declares all database entities.
    This will likely match with front-end code
"""
import datetime

from screaper_backend.application.application import db

# TODO: Add NOT NULL declarations

class Part(db.Model):
    # Whenever a new catalogue comes in, just append these parts! (and update the timestamp)
    __tablename__ = 'parts'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    part_external_identifier = db.Column(db.String)
    manufacturer_status = db.Column(db.String)
    manufacturer_price = db.Column(db.Float)
    manufacturer_stock = db.Column(db.Integer)
    manufacturer = db.Column(db.String)
    manufacturer_abbreviation = db.Column(db.String)
    weight_in_g = db.Column(db.Float)
    replaced_by = db.Column(db.String)

    changes = db.Column(db.Integer)
    shortcut = db.Column(db.String)
    hs_code = db.Column(db.String)
    important = db.Column(db.String)

    description_en = db.Column(db.String)
    description_de = db.Column(db.String)

    price_currency = db.Column(db.String)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Personal information
    user_name = db.Column(db.String)
    phone_number = db.Column(db.String)

    # Company information
    company_name = db.Column(db.String)
    domain_name = db.Column(db.String)
    fax_number = db.Column(db.String)
    email = db.Column(db.String)
    address = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)
    contact_name = db.Column(db.String)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))

    reference = db.Column(db.String)
    status = db.Column(db.String)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("parts.id"))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)
    origin = db.Column(db.String)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
