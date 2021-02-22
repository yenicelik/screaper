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

    def init(self):
        self.db = screaper_database

    def run_end_to_end_test(self):
        pass

    def item_set_1(self):
        # Get some random parts from the database
        itemset = [
            self.read_part_by_part_id_obj(2309).to_dict(),
            self.read_part_by_part_id_obj(1532).to_dict()
        ]
        print("itemset 1 is: ", itemset)
        return itemset



        itemset = [
            {
                "changes": -1,
                "cost_multiple": 2.5,
                "description_de": "STARTER KIT BC211/BCE311UA25",
                "description_en": "STARTER KIT BC211/BCE311UA25",
                "hs_code": "84529000000",
                "important": "",
                "id": 5314,
                "manufacturer": "Union Special",
                "manufacturer_abbreviation": "UNSP",
                "manufacturer_price": 545,
                "manufacturer_status": "A",
                "manufacturer_stock": 7,
                "part_external_identifier": "29480BC-BCE25",
                "price_currency": "EUR",
                "quantity": 3,
                "replaced_by": "",
                "sequence_order": 4.0000001,
                "shortcut": "",
                "item_single_price": 545 * 2.5,
                "total_final_price": 545 * 2.5 * 3,
                "total_final_profit": 545 * 2.5 * 3 - 545 * 3,
                "total_manufacturing_price": 545 * 3,
                "weight_in_g": 0
            }, {
                "changes": -1,
                "cost_multiple": 2.5,
                "description_de": "STARTER KIT BC211/BCE311P01",
                "description_en": "STARTER KIT BC211/BCE311P01",
                "hs_code": "84529000000",
                "id": 5311,
                "important": "",
                "manufacturer": "Union Special",
                "manufacturer_abbreviation": "UNSP",
                "manufacturer_price": 460,
                "manufacturer_status": "A",
                "manufacturer_stock": -1,
                "part_external_identifier": "29480BC-BCE01",
                "price_currency": "EUR",
                "quantity": 2,
                "replaced_by": "",
                "sequence_order": 2.0000001,
                "shortcut": "",
                "item_single_price": 460 * 2.5,
                "total_final_price": 460 * 2.5 * 2,
                "total_final_profit": 460 * 2.5 * 2 - 460 * 2,
                "total_manufacturing_price": 460 * 2,
                "weight_in_g": 0
            }
        ]
        return itemset

    def item_set_2(self):
        itemset = [
            {
                "changes": -1,
                "cost_multiple": 2.5,
                "description_de": "ZAHNRADSATZ",
                "description_en": "KIT OF GEARS",
                "hs_code": "",
                "id": 20934,
                "important": "",
                "manufacturer": "Union Special",
                "manufacturer_abbreviation": "UNSP",
                "manufacturer_price": 100.82,
                "manufacturer_status": "A",
                "manufacturer_stock": -1,
                "part_external_identifier": "995-401",
                "price_currency": "EUR",
                "quantity": 1,
                "replaced_by": "",
                "sequence_order": 1.0000001,
                "shortcut": "",
                "item_single_price": 100.82 * 2.5,
                "total_final_price": 100.82 * 2.5 * 2,
                "total_final_profit": 100.82 * 2.5 * 2 - 100.82 * 2,
                "total_manufacturing_price": 100.82 * 2,
                "weight_in_g": 0
            }, {
                "changes": -1,
                "cost_multiple": 2.5,
                "description_de": "HANDRADSCHUTZ",
                "description_en": "HANDWHEEL GUARD",
                "hs_code": "",
                "id": 7773,
                "important": "",
                "manufacturer": "Union Special",
                "manufacturer_abbreviation": "UNSP",
                "manufacturer_price": 0,
                "manufacturer_status": "T",
                "manufacturer_stock": -1,
                "part_external_identifier": "35021B",
                "price_currency": "EUR",
                "quantity": 0,
                "replaced_by": "",
                "sequence_order": 2.0000001,
                "shortcut": "",
                "item_single_price": 0 * 2.5,
                "total_final_price": 0,
                "total_final_profit": 0,
                "total_manufacturing_price": 0,
                "weight_in_g": 26
            }, {
                "changes": -1,
                "cost_multiple": 2.5,
                "description_de": "JETZT 34727 XX8",
                "description_en": "PRS FOOT ASS",
                "hs_code": "",
                "id": 7081,
                "important": "",
                "manufacturer": "Union Special",
                "manufacturer_abbreviation": "UNSP",
                "manufacturer_price": 0,
                "manufacturer_status": "G",
                "manufacturer_stock": -1,
                "part_external_identifier": "34720XX8",
                "price_currency": "EUR",
                "quantity": 0,
                "replaced_by": "",
                "sequence_order": 1.0000001,
                "shortcut": "HP",
                "item_single_price": 0 * 2.5,
                "total_final_price": 0,
                "total_final_profit": 0,
                "total_manufacturing_price": 0,
                "weight_in_g": 125
            }
        ]
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
                assert order_item["id"] in (5, 100, 52, 53, 23, 64, 24, 64, 75, 86, 7081, 7773, 5314, 5311, 20934), ("part is not correctly set!", order_item)

        for order in orders:
            for order_item in order["items"]:
                print("rel part is:", order_item)
                assert order_item["part_external_identifier"] in (
                    "29480BC-BCE25",
                    "29480BC-BCE01",
                    "995-401",
                    "35021B",
                    "34720XX8",
                    "10005",
                    "10030KU",
                    "10021S",
                    "10022",
                    "10013CDA",
                    "10022L",
                    "10016",
                    "10022L",
                    "10024BU",
                    "10030AU",

                    # TODO: Should double check if these are in-order to be here!
                    # Or if there is a bug with import (I think it's a bug that will be replaced by using the DB)

                    # "29480BC-BCE16",
                    # "29480BC24",
                    # "35021",
                    # "34720XX16"
                ), ("part is not correctly set!", order_item["part_external_identifier"], order_item)

                # Will make a manual test now

        # References are correctly inserted
        for order in orders:
            assert order["reference"] in ("ref MCY-GLS", "REF MCY-GÜLSAN", "REF MCY-KAYSERI"), order
            assert order["user_name"] in ("default", "kayseri_sentetik", "gulsan_sentetik"), order

        # Number of items in orders are correct


if __name__ == '__main__':
    unittest.main()
