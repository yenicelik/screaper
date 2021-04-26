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
    def create_order(self, customer_email, reference, shipment_address, order_items, note, files):

        if files is not None:
            assert isinstance(files, dict), files

        # Get customer object
        customer = screaper_database.read_customers_by_customer_email(email=customer_email)

        order = screaper_database.create_single_order(
            customer=customer,
            reference=reference,
            shipment_address=shipment_address,
            note=note
        )
        i = 0
        for order_item in order_items:
            i += 1
            assert "id" in order_item, order_item

            part = screaper_database.read_part_by_part_id_obj(idx=order_item["id"])

            # TODO: Fetch the part as given by the external identifier
            print("Inserting: ", order_item)
            # Gotta replace the price by internally feteched price
            screaper_database.create_order_item(
                order=order,
                part=part,
                quantity=order_item["quantity"],
                item_single_price=None, #  order_item["item_single_price"]
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

    def edit_order_by_customer(
            self,
            customer_email,
            order_id,
            tax_rate=None,
            absolute_discount=None,
            note=None,
            date_submitted=None,
            valid_through_date=None,
            expected_delivery_date=None,
            reference=None,
            shipment_address=None,
            files=None,
            paid_date=None,
            total_price=None,
            currency=None,
            order_items=None,
    ):
        # Double check if the order id belongs to the current user!


        if files is not None:
            assert isinstance(files, dict), files

        # Get customer object
        customer = screaper_database.read_customers_by_customer_email(email=customer_email)

        # Read orders by order_id AND customer id
        existing_order = screaper_database.read_order_exists_by_customer(order_id=order_id, customer_id=customer.id)

        # Now you can create a new object for the input
        # Anything that is not None, can be input, and the rest needs to be updated
        new_input_object = {
            tax_rate: tax_rate if tax_rate is not None else existing_order.tax_rate,
            absolute_discount: absolute_discount if absolute_discount is not None else existing_order.absolute_discount,
            note: note if note is not None else existing_order.note,
            date_submitted: date_submitted if date_submitted is not None else existing_order.date_submitted,
            valid_through_date: valid_through_date if valid_through_date is not None else existing_order.valid_through_date,
            expected_delivery_date: expected_delivery_date if expected_delivery_date is not None else existing_order.expected_delivery_date,
            reference: reference if reference is not None else existing_order.reference,
            shipment_address: shipment_address if shipment_address is not None else existing_order.shipment_address,
            paid_date: paid_date if paid_date is not None else existing_order.paid_date,
            total_price: total_price if total_price is not None else existing_order.total_price,
            currency: currency if currency is not None else existing_order.currency,
        }

        screaper_database.update_single_order(**new_input_object)

        # Then, also look at the files and the
        # Overwrite files if any files array was provided
        # Overwrite parts if any parts array was provided
        i = 0
        if order_items:
            # Easiest to just delete, and override
            screaper_database.drop_order_items_for_order(existing_order)
            for order_item in order_items:
                i += 1
                assert "id" in order_item, order_item

                part = screaper_database.read_part_by_part_id_obj(idx=order_item["id"])

                # get the order item id

                # probably easiest to just delete everything, and re-instantiate all again


                # TODO: Fetch the part as given by the external identifier
                print("Inserting: ", order_item)
                # Gotta replace the price by internally feteched price
                screaper_database.create_order_item(
                    order=existing_order,
                    part=part,
                    quantity=order_item["quantity"],
                    item_single_price=order_item["item_single_price"]
                )

        if files:
            screaper_database.drop_files_for_order(existing_order)
            print(f"Crated {i} new order items")
            i = 0
            for filename, file in files.items():
                i += 1
                assert isinstance(file, FileStorage), (file, type(file))
                screaper_database.create_file_item(
                    order=existing_order,
                    file=base64.b64encode(file.read()),
                    filename=filename
                )

        screaper_database.session.commit()

        # Make sure that there are more items in the database now (?)


model_orders = Orders()
