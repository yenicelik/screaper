"""
    Database
"""
from sqlalchemy import create_engine, MetaData

from screaper_backend.entities.entities_db import OrderItem, Order, Product, Customer


class Database:

    def __init__(self):
        # Create sqlalchemy database connection
        self.engine = create_engine('sqlite:///:memory:')

        # Drop all tables (because this is still in development
        tables = [
            Product,
            Customer,
            Order,
            OrderItem
        ]
        metadata = MetaData(self.engine)
        metadata.create_all()

        # Create all tables (DEV)

        # Populate tables (?) Probably not, actually
        pass



if __name__ == "__main__":
    print("Starting to create databsse connection")
