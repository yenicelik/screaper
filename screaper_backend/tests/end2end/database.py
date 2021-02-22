"""
    Unit Tests for
"""

import unittest
from random import random

from screaper_backend.application.application import db

from screaper_backend.models.customers import model_customers
from screaper_backend.models.orders import model_orders
from screaper_backend.resources.database import screaper_database


class TestDatabase(unittest.TestCase):

    def item_set_1(self):
        # Get some random parts from the database
        print("inserting: ", screaper_database.read_part_by_part_id_obj(2309).to_dict())
        print("inserting: ", screaper_database.read_part_by_part_id_obj(1532).to_dict())
        itemset = [
            screaper_database.read_part_by_part_id_obj(2309).to_dict(),
            screaper_database.read_part_by_part_id_obj(1532).to_dict()
        ]
        itemset[0].update({
                "quantity": 2,
                "item_single_price": 55.3,
                "id": 2309
            })
        itemset[1].update({
                "quantity": 3,
                "item_single_price": 95.3,
                "id": 1532
            })
        for x in itemset:
            print("itemset 1 is: ", x)
        return itemset

    def item_set_2(self):
        print("inserting: ", screaper_database.read_part_by_part_id_obj(5314).to_dict())
        print("inserting: ", screaper_database.read_part_by_part_id_obj(5311).to_dict())
        print("inserting: ", screaper_database.read_part_by_part_id_obj(20934).to_dict())

        itemset = [
            screaper_database.read_part_by_part_id_obj(5314).to_dict(),
            screaper_database.read_part_by_part_id_obj(5311).to_dict(),
            screaper_database.read_part_by_part_id_obj(20934).to_dict()
        ]
        itemset[0].update({
                "quantity": 12,
                "item_single_price": 102.3,
                "id": 5314
            })
        itemset[1].update({
                "quantity": 53,
                "item_single_price": 2.34,
                "id": 5311
            })
        itemset[2].update({
                "quantity": 6,
                "item_single_price": 102.3,
                "id": 20934
            })
        for x in itemset:
            print("itemset 2 is: ", x)
        return itemset

    def test_order_submit(self):

        customer_username = "gulsan_sentetik"
        reference = "REF MCY-GÜLSAN"
        items = self.item_set_1()

        # Insert this into the database
        model_orders.create_order(
            customer_username=customer_username,
            reference=reference,
            order_items=items
        )

        customer_username = "kayseri_sentetik"
        reference = "REF MCY-KAYSERI"
        items = self.item_set_2()

        # Insert this into the database
        model_orders.create_order(
            customer_username=customer_username,
            reference=reference,
            order_items=items
        )

        # Check number of customers
        customers = model_customers.customers()
        assert len(customers) == 3, (len(customers), customers)

        # Check number of orders
        orders = model_orders.orders()
        assert len(orders) == 3, (len(orders), orders)

        # Check number of orderitems
        order_items = []
        for order in orders:
            print("Returned order is", order)
            for order_item in order["items"]:
                order_items.append(order_item)

        assert len(order_items) == 2 + 3 + 10, (len(order_items), order_items)

        # Check that orderitems correspond to partnames
        for order in orders:
            for order_item in order["items"]:
                print("rel part is:", order_item)
                assert order_item["id"] in (5, 100, 52, 53, 23, 64, 24, 64, 75, 86, 2309, 1532, 7773, 5314, 5311, 20934), ("part is not correctly set!", order_item)

        for order in orders:
            for order_item in order["items"]:
                print("rel part is:", order_item)
                assert order_item["part_external_identifier"] in (

                    # from the database inserts from before
                    "10-4",
                    "10030KH",
                    "10021FN",
                    "10021G",
                    "10013A",
                    "10022J",
                    "10013CD",
                    "10022J",
                    "10024BD",
                    "10030A",

                    # from now inserted items
                    "13430B",
                    "18-934",
                    "29480BC-BCE25D",
                    "29480BC-BCE15",
                    "995-518"

                    # "18-752",
                    # "13440607",
                    # "29480BC-BCE16",
                    # "29480BC24",
                    # "995-401"

                    # "29480BC-BCE25",
                    # "29480BC-BCE01",
                    # "995-401",
                    # "35021B",
                    # "34720XX8",
                    # "10005",
                    # "10030KU",
                    # "10021S",
                    # "10022",
                    #
                    #
                    # "10013CDA",
                    # "10022L",
                    # "10016",
                    # "10022L",
                    # "10024BU",
                    # "10030AU",

                    # TODO: Should double check if these are in-order to be here!
                    # Or if there is a bug with import (I think it's a bug that will be replaced by using the DB)

                ), ("part is not correctly set!", order_item["part_external_identifier"], order_item)

                # Will make a manual test now

        # References are correctly inserted
        for order in orders:
            assert order["reference"] in ("ref MCY-GLS", "REF MCY-GÜLSAN", "REF MCY-KAYSERI"), order
            assert order["user_name"] in ("default", "kayseri_sentetik", "gulsan_sentetik"), order

        # Number of items in orders are correct


if __name__ == '__main__':
    unittest.main()
