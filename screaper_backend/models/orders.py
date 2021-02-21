"""
    Get orders for a certain user
"""
from dotenv import load_dotenv

from screaper_backend.resources.database import screaper_database

load_dotenv()


class Orders:

    def __init__(self):
        self._orders = screaper_database.read_orders()
        print(f"{len(self._orders)} orders collected")

    def orders(self):
        self._orders = screaper_database.read_orders()
        return self._orders

    def create_order(self, customer_username, reference, order_items):
        # Get customer object
        customer = screaper_database.read_customers_by_customer_username(username=customer_username)

        order = screaper_database.create_single_order(customer=customer, reference=reference)
        i = 0
        for order_item in order_items:
            i += 1
            assert "part_external_identifier" in order_item

            part = screaper_database.read_part_by_part_external_identifier_obj(external_identifier=order_item["part_external_identifier"])

            # TODO: Fetch the part as given by the external identifier
            print("Inserting: ", order_item)
            screaper_database.create_order_item(
                order=order,
                part=part,
                quantity=order_item["quantity"],
                item_price=order_item["item_single_price"]
            )

        screaper_database.session.commit()

        print(f"Crated {i} new order items")

        # Make sure that there are more items in the database now (?)


model_orders = Orders()
