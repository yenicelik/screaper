"""
    Get orders for a certain user
"""
import base64

from dotenv import load_dotenv
from werkzeug.datastructures import FileStorage

from screaper_backend.resources.database import screaper_database

load_dotenv()


class Orders:

    def __init__(self):
        self._orders = screaper_database.read_orders()
        print(f"{len(self._orders)} orders collected")

    def orders(self):
        self._orders = screaper_database.read_orders()
        return self._orders

    def orders_by_user(self, user_email):
        self._orders = screaper_database.read_orders_by_user(user_email=user_email)
        return self._orders

    # Also insert files if there are any
    def create_order(self, customer_email, reference, order_items, files):

        if files is not None:
            assert isinstance(files, dict), files

        # Get customer object
        customer = screaper_database.read_customers_by_customer_email(email=customer_email)

        order = screaper_database.create_single_order(customer=customer, reference=reference)
        i = 0
        for order_item in order_items:
            i += 1
            assert "id" in order_item, order_item

            part = screaper_database.read_part_by_part_id_obj(idx=order_item["id"])

            # TODO: Fetch the part as given by the external identifier
            print("Inserting: ", order_item)
            screaper_database.create_order_item(
                order=order,
                part=part,
                quantity=order_item["quantity"],
                item_single_price=order_item["item_single_price"]
            )

        print(f"Crated {i} new order items")
        i = 0
        for filename, file in files.items():
            i += 1
            assert isinstance(file, FileStorage), (file, type(file))
            screaper_database.create_file_item(
                order=order,
                file=base64.b64encode(file.read()),
                filename=filename
            )

        screaper_database.session.commit()

        # Make sure that there are more items in the database now (?)


model_orders = Orders()
