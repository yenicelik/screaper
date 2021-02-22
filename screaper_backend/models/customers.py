"""
    Get all customers in the system
"""
from dotenv import load_dotenv

from screaper_backend.resources.database import screaper_database

load_dotenv()


class Customers:

    def __init__(self):
        self._customers = screaper_database.read_customers()
        print(f"{len(self._customers)} customers collected")

    def customers(self):
        return self._customers

    def customer_usernames(self):
        return set(x["user_name"]for x in self._customers)


model_customers = Customers()
