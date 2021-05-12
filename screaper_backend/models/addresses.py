"""
    Get all addresses in the system
"""
from dotenv import load_dotenv

from screaper_backend.resources.database import screaper_database

load_dotenv()

# TODO Modify to get addresses
class Addresses:

    def __init__(self):
        self._addresses = screaper_database.read_customers()
        print(f"{len(self._addresses)} customers collected")

    def addresses(self):
        return screaper_database.read_addresses()

    def address_by_user_email(self, email):
        return screaper_database.read_addresses_by_customer_email(email=email)


model_addresses = Addresses()
