"""
    Get all customers in the system
"""
import yaml
import os

from dotenv import load_dotenv

load_dotenv()

class Customers:

    def __init__(self):
        print("Current pwd is: ", os.getcwd(), os.listdir(os.getcwd()))
        with open(os.getenv("MOCK_CUSTOMERS"), "r") as f:
            loaded_yaml_file = yaml.load(f, Loader=yaml.Loader)['customers']

        self._orders = loaded_yaml_file

    def orders(self):
        return self._orders


model_customers = Customers()
