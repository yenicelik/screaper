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
        print("Customer usernames are: ", [x["user_name"] for x in self._customers])
        return set(x["user_name"]for x in self._customers)

    def customer_emails(self):
        print("Customer emails are: ", [x["email"] for x in self._customers])
        return set(x["email"]for x in self._customers)

    def customer_by_username(self, username):
        return screaper_database.read_customers_by_customer_username(username=username)


model_customers = Customers()
