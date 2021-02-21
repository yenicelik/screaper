"""
    Get all customers in the system
"""
from dotenv import load_dotenv

from screaper_backend.resources.database import screaper_database

load_dotenv()


class Customers:

    def __init__(self):
        self._customers = screaper_database.read_customers()
        print("self orders are: ", self._customers)

    def customers(self):
        return self._customers


model_customers = Customers()
