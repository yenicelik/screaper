"""
    Declares all database entities.
    This will likely match with front-end code
"""
import datetime

import enum
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.sql import func

from screaper_backend.application import db


class StatusType(enum.Enum):
    APPLE = "Crunchy apple"
    BANANA = "Sweet banana"


class Part(db.Model, SerializerMixin):
    # Whenever a new catalogue comes in, just append these parts! (and update the timestamp)
    __tablename__ = 'parts'
    serialize_rules = ("-_children", "-rel_part")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # part_uuid = db.Column(db.String, unique=True, nullable=False)

    part_external_identifier = db.Column(db.String, nullable=False)
    manufacturer_status = db.Column(db.String)
    manufacturer_price = db.Column(db.Float)
    manufacturer_stock = db.Column(db.Integer)
    manufacturer = db.Column(db.String)
    manufacturer_abbreviation = db.Column(db.String)
    weight_in_g = db.Column(db.Float)
    replaced_by = db.Column(db.String)

    searchstring = db.Column(db.String, nullable=False)

    changes = db.Column(db.Integer)
    shortcut = db.Column(db.String)
    hs_code = db.Column(db.String)
    important = db.Column(db.String)

    description_en = db.Column(db.String)
    description_de = db.Column(db.String)

    price_currency = db.Column(db.String)

    created_at = db.Column(db.DateTime, server_default=func.now())

    _children = db.relationship('OrderItem', back_populates="rel_part")


class Customer(db.Model, SerializerMixin):
    # These are also the users
    # TODO: Implement some unique user-id to this! e-mail is probably alright,
    # but then everyone needs to have an e-mail
    __tablename__ = "customers"
    serialize_rules = ("-rel_orders", "-owner")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Personal information
    # Use as UUID
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

    created_at = db.Column(db.DateTime, server_default=func.now())

    rel_orders = db.relationship('Order', backref='owner')


class Order(db.Model, SerializerMixin):
    __tablename__ = "orders"
    serialize_rules = ("-rel_files", "-rel_order_items", "-owner", "-order")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)

    reference = db.Column(db.String, nullable=False)
    shipment_address = db.Column(db.String, nullable=False)
    note = db.Column(db.String)

    # All these things will be null at start
    expected_delivery_date = db.Column(db.String)
    absolute_discount = db.Column(db.Float, default=0.00, nullable=False)
    tax_rate = db.Column(db.Float, default=0.18, nullable=False)
    currency = db.Column(db.String, default="EUR", nullable=False)

    origin = db.Column(db.String)
    paid_on_date = db.Column(db.String)

    total_price_including_discount_and_taxrate = db.Column(db.Float)

    valid_through_date = db.Column(db.DateTime,
                                   default=lambda x: datetime.datetime.utcnow() + datetime.timedelta(days=21))

    # Is one of: waiting_for_offer, waiting_for_confirmation, waiting_for_delivery, delivery_sent
    status = db.Column(Enum("PERSON", "NORP", "FACILITY", "ORGANIZATION", "GPE", "LOCATION", "PRODUCT", "EVENT", "WORK OF ART", "LAW",
             "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL", "OTHER",
             name="ner_types_enum"), default="waiting_for_offer", nullable=False)  # Have a limited number of 'stati' here

    date_submitted = db.Column(db.DateTime, server_default=func.now())
    created_at = db.Column(db.DateTime, server_default=func.now())

    rel_order_items = db.relationship('OrderItem', backref='owner')

    rel_files = db.relationship('FileRecord', back_populates='order')


class OrderItem(db.Model, SerializerMixin):
    __tablename__ = 'order_items'
    serialize_rules = ("-rel_part", "-_children")

    rel_part = db.relationship("Part", uselist=False, back_populates="_children")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # order_item_uuid = db.Column(db.String, nullable=False)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey("parts.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    item_list_price = db.Column(db.Float, nullable=True)
    item_single_including_margin_price = db.Column(db.Float, nullable=True)

    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)


class FileRecord(db.Model, SerializerMixin):
    __tablename__ = "files"
    serialize_rules = ("-rel_files", "-order")

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # file_uuid = db.Column(db.String, unique=True, nullable=False)

    file = db.Column(db.LargeBinary(), nullable=False)
    filename = db.Column(db.String(), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

    order = db.relationship("Order", back_populates="rel_files")
