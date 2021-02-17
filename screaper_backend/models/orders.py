"""
    Get orders for a certain user
"""
import yaml
import os

from dotenv import load_dotenv

from screaper_backend.resources.database import screaper_database

load_dotenv()

class Orders:

    def __init__(self):
        print("Current pwd is: ", os.getcwd(), os.listdir(os.getcwd()))

        # get all from the database
        # with open(os.getenv("MOCK_ORDERS"), "r") as f:
        #     loaded_yaml_file = yaml.load(f, Loader=yaml.Loader)['orders']

        # self._orders = loaded_yaml_file

        self._orders = screaper_database.read_orders()
        print("self orders are: ", self._orders)

    def orders(self):
        return self._orders


model_orders = Orders()
