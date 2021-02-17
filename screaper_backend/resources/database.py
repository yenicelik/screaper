"""
    Database
"""

from screaper_backend.application.application import db
from screaper_backend.entities.entities_db import OrderItem, Order, Part, Customer
from screaper_backend.importer.data_importer_unionspecial import DataImporterUnionSpecial


class Database:
    """
        Only CRUD functions should be implemented here
        Create
        Read
        Update
        Delete
    """

    def __init__(self, dev=True):
        # Create sqlalchemy database connection
        self.db = db

        # # Drop all tables (because this is still in development
        # tables = [
        #     Part,
        #     Customer,
        #     Order,
        #     OrderItem
        # ]

        # Create all tables (DEV)
        if dev:
            db.create_all()

        self.session = self.db.session

        # Populate tables (?) Probably not, actually
        self._populate_union_special_partslist_into_db()
        self._create_mock_customers()
        self._create_mock_order()

        # Count number of items in the tables
        print("Count Order: ", self.session.query(Order).count())
        print("Count Order: ", self.session.query(Order.id).all())
        print("Count OrderItem: ", self.session.query(OrderItem).count())
        print("Count OrderItem: ", self.session.query(OrderItem.id).all())
        print("Count Parts: ", self.session.query(Part).count())
        print("Count Parts: ", self.session.query(Part.id).all())
        print("Count Customers: ", self.session.query(Customer).count())
        print("Count Customers (All): ", self.session.query(Customer.id).all())

    def _populate_union_special_partslist_into_db(self):
        """
            Populates the database with the union special price list
        :return:
        """
        data = DataImporterUnionSpecial().parts_list()
        # Only keep valid keys:
        data = data.drop(columns=["searchstring"])
        # Push this into the table
        objs = []
        for obj in data.to_dict("records"):
            tmp = Part(**obj)
            objs.append(tmp)
        self.session.bulk_save_objects(objs)
        self.session.commit()

    def _create_mock_order(self):
        """
            Create some mock elements:
            - Create a single customer. This is the placeholder for all customers now
        :return:
        """
        order = self.create_single_order(customer_id=1, reference="ref MCY-GLS")
        print("Created order with orderid: ", order.id)
        self.create_order_item(
            order_id=order.id,
            part_id=5,
            quantity=50,
            price=50,
            origin="DE / US"
        )
        self.session.commit()

    def _create_mock_customers(self):
        """
            Create some mock elements:
            - Create a single customer. This is the placeholder for all customers now
        :return:
        """
        self.create_customer(
            user_name="gulsan_sentetik",
            company_name="GÜLSAN SENTETİK DOKUMA SAN. VE TİC.A.Ş.",
            phone_number="(0342) 337 11 80",
            fax_number="(0342) 337 25 28",
            domain_name="",
            email="",
            address="",
            city="GAZİANTEP",
            country="",
            contact_name="Sn.Tuğba YILDIRIM"
        )
        self.create_customer(
            user_name="kayseri_sentetik",
            company_name="KAYSERI ŞEKER FABRIKASI A.Ş.",
            phone_number="(0-352) 331 24 00 (6 hat)",
            fax_number="(0-352) 331 24 06",
            domain_name="kayseriseker.com.tr",
            email="haberlesme@kayseriseker.com.tr",
            address="Osman Kavuncu Cad. 7. KM 38070 Kocasinan",
            city="KAYSERI",
            country="",
            contact_name=""
        )
        self.session.commit()

    ########################
    # CREATE Operations
    ########################
    def create_customer(
            self,
            user_name,
            company_name,
            phone_number,
            fax_number,
            domain_name,
            email,
            address,
            city,
            country,
            contact_name
    ):
        assert user_name, user_name
        assert company_name, company_name
        assert phone_number, phone_number
        assert fax_number, fax_number
        # assert domain_name, domain_name
        # assert email, email
        # assert address, address
        # assert city, city
        # assert country, country
        # assert contact_name, contact_name

        # Make some type-tests, fail if not sufficient
        customer = Customer(
            user_name=user_name,
            company_name=company_name,
            phone_number=phone_number,
            fax_number=fax_number,
            domain_name=domain_name,
            email=email,
            address=address,
            city=city,
            country=country,
            contact_name=contact_name
        )
        self.session.add(customer)
        self.session.commit()
        self.session.refresh(customer)
        assert customer.id
        return customer

    def create_oder(self, order, order_items):

        assert order, order
        assert order_items, order_items

        order = self.create_single_order(order.customer_id, order.reference)
        for order_item in order_items:
            self.create_order_item(
                part_id=order_item.part_id,
                order_id=order.id,
                quantity=order_item.quantity,
                price=order_item.price,
                origin=order_item.origin
            )

    def create_single_order(
            self,
            customer_id,
            reference
    ):
        # Make some type-tests, fail if not sufficient
        assert customer_id is not None, customer_id
        assert reference, reference

        order = Order(
            customer_id=customer_id,
            reference=reference,
            status="offer created"
        )
        self.session.add(order)
        self.session.commit()
        self.session.refresh(order)
        assert order.id
        return order

    def create_order_item(
            self,
            order_id,
            part_id,
            quantity,
            price,
            origin
    ):
        # Make some type-tests, fail if not sufficient
        order_item = OrderItem(
            order_id=order_id,
            part_id=part_id,
            quantity=quantity,
            price=price,
            origin=origin
        )
        self.session.add(order_item)
        self.session.commit()
        self.session.refresh(order_item)
        assert order_item.id
        return order_item


    ########################
    # READ Operations
    ########################
    def read_customers(self):
        customers = self.session.query(Customer).all()
        return customers
    #
    # # TODO: Should be sorted by a user uuid
    # def read_orders(self):
    #     # Join with Customers, OrderItems, and Parts?
    #     orders = self.session.query(Customer, Order) \
    #         .filter(Customer.id == Order.customer_id) \
    #         .all()
    #
    #     # customers, orders, order_items, parts
    #     print("Retrieved orders are: ", orders)
    #
    #     for order in orders:
    #         print("Order is: ", order)
    #
    #     return orders

    # TODO: Should be searching by an Order ID
    # def read_detailed_orders(self):
    #     # Join with Customers, OrderItems, and Parts?
    #     # orders = self.session.query(Customer, Order, OrderItem, Part) \
    #     #     .filter(Customer.id == Order.customer_id) \
    #     #     .filter(Order.id == OrderItem.order_id) \
    #     #     .filter(OrderItem.part_id == Part.id) \
    #     #     .all()
    #
    #     orders = self.session.query(Customer, Order) \
    #         .filter(Customer.id == Order.customer_id) \
    #         .filter(Order.id == OrderItem.order_id) \
    #         .filter(OrderItem.part_id == Part.id) \
    #         .all()
    #
    #     # customers, orders, order_items, parts
    #     print("Retrieved orders are: ", orders)
    #
    #     for order in orders:
    #         print("Order is: ", order)
    #
    #     return orders

    def read_orders(self):
        customers = self.session.query(Customer).all()

        print("Customers are: ", customers)

        # Expand this object to a tree-like structure
        out = []
        for customer in customers:
            print(customer)
            print(customer.rel_orders)
            for order in customer.rel_orders:
                tmp1 = order.to_dict()
                print("tmp is: ")
                print(tmp1)
        #         tmp1.update(customer.to_dict())
        #         tmp1['items'] = []
        #         for order_item in order.rel_order_items:
        #             tmp2 = order_item.to_dict()
        #             tmp2.update(order_item.rel_part.to_dict())
        #             tmp1['items'].append(tmp2)
        #             print("Adding following object to the list (1):")
        #             print(tmp2)
        #         print("Adding following object to the list (2):")
        #         print(tmp1)
        #         out.append(tmp1)

        print("Out length is: ", len(out))
        print("Out length is: ", out[0])
        print("Out length is: ", out)

        return out




    ########################
    # UPDATE Operations
    ########################

    ########################
    # DELETE Operations
    ########################

    # TODO: Ignore for now. No new products should be added to the system for now
    # def create_product(
    #         self,
    #         product_external_identifier,
    #         manufacturer_status,
    #         manufacturer_price,
    #         price_currency,
    #         manufacturer,
    #         manufacturer_abbreviation,
    #         weight_in_g,
    #         replaced_by,
    #         changes,
    #         shortcut,
    #         hs_code,
    #         important,
    #         description_en,
    #         description_de
    # ):
    #     # Make some type-tests, fail if not sufficient
    #     product = Part(
    #         product_external_identifier=product_external_identifier,
    #         manufacturer_status=manufacturer_status,
    #         manufacturer_price=manufacturer_price,
    #         price_currency=price_currency,
    #         manufacturer=manufacturer,
    #         manufacturer_abbreviation=manufacturer_abbreviation,
    #         weight_in_g=weight_in_g,
    #         replaced_by=replaced_by,
    #         changes=changes,
    #         shortcut=shortcut,
    #         hs_code=hs_code,
    #         important=important,
    #         description_en=description_en,
    #         description_de=description_de
    #     )
    #     self.session.add(product)


screaper_database = Database()

if __name__ == "__main__":
    print("Starting to create databsse connection")
    database = Database()
    print("Successfully created and populated the database")
