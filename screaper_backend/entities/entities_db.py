"""
    Declares all database entities.
    This will likely match with front-end code
"""
import datetime

from sqlalchemy_serializer import SerializerMixin

from screaper_backend.application import db

class Part(db.Model, SerializerMixin):
    # Whenever a new catalogue comes in, just append these parts! (and update the timestamp)
    __tablename__ = 'parts'
    serialize_rules = ("-_children", "-rel_part")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    part_external_identifier = db.Column(db.String, nullable=False)
    manufacturer_status = db.Column(db.String)
    manufacturer_price = db.Column(db.Float)
    manufacturer_stock = db.Column(db.Integer)
    manufacturer = db.Column(db.String)
    manufacturer_abbreviation = db.Column(db.String)
    weight_in_g = db.Column(db.Float)
    replaced_by = db.Column(db.String)

    searchstring = db.Column(db.String, nullable=False)

    origin = db.Column(db.String)
    changes = db.Column(db.Integer)
    shortcut = db.Column(db.String)
    hs_code = db.Column(db.String)
    important = db.Column(db.String)

    description_en = db.Column(db.String)
    description_de = db.Column(db.String)

    price_currency = db.Column(db.String)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    _children = db.relationship('OrderItem', back_populates="rel_part")


class Customer(db.Model, SerializerMixin):
    # These are also the users
    # TODO: Implement some unique user-id to this! e-mail is probably alright,
    # but then everyone needs to have an e-mail
    __tablename__ = "customers"
    serialize_rules = ("-rel_orders", "-owner")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Personal information
    user_name = db.Column(db.String, index=True, unique=True)
    # The email is the respective username, which we use to connect this with an order
    email = db.Column(db.String, index=True, unique=True)

    # Company information
    company_name = db.Column(db.String)
    domain_name = db.Column(db.String)
    phone_number = db.Column(db.String)
    fax_number = db.Column(db.String)
    address = db.Column(db.String)
    city = db.Column(db.String)
    country = db.Column(db.String)
    contact_name = db.Column(db.String)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    rel_orders = db.relationship('Order', backref='owner')


class Order(db.Model, SerializerMixin):
    __tablename__ = "orders"
    serialize_rules = ("-rel_files", "-rel_order_items", "-owner", "-order")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))

    reference = db.Column(db.String)
    status = db.Column(db.String)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    rel_order_items = db.relationship('OrderItem', backref='owner')

    rel_files = db.relationship('FileRecord', back_populates='order')


class OrderItem(db.Model, SerializerMixin):
    __tablename__ = 'order_items'
    serialize_rules = ("-rel_part", "-_children")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    part_id = db.Column(db.Integer, db.ForeignKey("parts.id"))
    quantity = db.Column(db.Integer)
    item_single_price = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    rel_part = db.relationship("Part", uselist=False, back_populates="_children")


class FileRecord(db.Model, SerializerMixin):
    __tablename__ = "files"
    serialize_rules = ("-rel_files", "-order")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    file = db.Column(db.LargeBinary(), nullable=False)
    filename = db.Column(db.String(), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

    order = db.relationship("Order", back_populates="rel_files")

