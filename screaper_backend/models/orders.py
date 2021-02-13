"""
    Get orders for a certain user
"""
import yaml


class Orders:

    def __init__(self):
        with open("/Users/david/screaper/screaper_backend/mockups_order.yaml", "r") as f:
            loaded_yaml_file = yaml.load(f, Loader=yaml.Loader)['orders']

        self._orders = loaded_yaml_file

    def orders(self):
        return self._orders

model_orders = Orders()
