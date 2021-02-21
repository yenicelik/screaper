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

        # Get first customer
        customer = self.read_customers_obj()[0]

        order = self.create_single_order(customer=customer, reference="ref MCY-GLS")
        print("Created order with orderid: ", order.id)

        # print parts that we're gonna input:
        part = self.read_part_by_part_id_obj(5)
        print("buying part: ", part)
        self.create_order_item(
            order=order,
            part=part,
            quantity=50,
            item_price=50,
        )
        part = self.read_part_by_part_id_obj(100)
        print("buying part: ", part.to_dict())
        self.create_order_item(
            order=order,
            part=part,
            quantity=12,
            item_price=684.13 * 2.5,
        )
        part = self.read_part_by_part_id_obj(52)
        print("buying part: ", part.to_dict())
        self.create_order_item(
            order=order,
            part=part,
            quantity=12,
            item_price=100 * 2.5,
        )
        part = self.read_part_by_part_id_obj(53)
        print("buying part: ", part.to_dict())
        self.create_order_item(
            order=order,
            part=part,
            quantity=12,
            item_price=100 * 2.5,
        )
        part = self.read_part_by_part_id_obj(23)
        print("buying part: ", part.to_dict())
        self.create_order_item(
            order=order,
            part=part,
            quantity=12,
            item_price=100 * 2.5,
        )
        part = self.read_part_by_part_id_obj(64)
        print("buying part: ", part.to_dict())
        self.create_order_item(
            order=order,
            part=part,
            quantity=12,
            item_price=100 * 2.5,
        )
        part = self.read_part_by_part_id_obj(24)
        print("buying part: ", part.to_dict())
        self.create_order_item(
            order=order,
            part=part,
            quantity=12,
            item_price=100 * 2.5,
        )
        part = self.read_part_by_part_id_obj(64)
        print("buying part: ", part.to_dict())
        self.create_order_item(
            order=order,
            part=part,
            quantity=12,
            item_price=100 * 2.5,
        )
        part = self.read_part_by_part_id_obj(75)
        print("buying part: ", part.to_dict())
        self.create_order_item(
            order=order,
            part=part,
            quantity=12,
            item_price=100 * 2.5,
        )
        part = self.read_part_by_part_id_obj(86)
        print("buying part: ", part.to_dict())
        self.create_order_item(
            order=order,
            part=part,
            quantity=12,
            item_price=100 * 2.5,
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

    def create_order(self, order, order_items):

        assert order, order
        assert order_items, order_items

        order = self.create_single_order(order.customer_id, order.reference)
        for order_item in order_items:
            self.create_order_item(
                part_id=order_item.part_id,
                order=order,
                quantity=order_item.quantity,
                item_price=order_item.item_price
            )

    def create_single_order(
            self,
            customer,
            reference
    ):
        # Make some type-tests, fail if not sufficient
        assert customer is not None, customer
        assert reference, reference

        order = Order(
            owner=customer,
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
            order,
            part,
            quantity,
            item_price
    ):
        # Make some type-tests, fail if not sufficient
        order_item = OrderItem(
            owner=order,
            rel_part=part,
            quantity=quantity,
            item_price=item_price
        )
        self.session.add(order_item)
        self.session.commit()
        self.session.refresh(order_item)
        assert order_item.id
        return order_item

    ########################
    # READ Operations
    ########################
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
                # print("tmp is: ")
                # print(tmp1)
                tmp1.update(customer.to_dict())
                tmp1['items'] = []
                # print("tmp after is: ")
                print(tmp1)
                for order_item in order.rel_order_items:
                    tmp2 = order_item.to_dict()
                    del tmp2['owner']
                    tmp2.update(order_item.rel_part.to_dict())
                    # print("tmp 2 is: ", tmp2)
                    tmp1['items'].append(tmp2)
                    # print("Adding following object to the list (1):")
                    print(tmp2)
                # print("Adding following object to the list (2):")
                print(tmp1)
                out.append(tmp1)

        # print("Out length is: ", len(out))
        # print("Out length is: ", out[0])
        # print("Out length is: ", out)

        return out

    def read_customers(self):
        customers = self.session.query(Customer).all()

        print("Customers are: ", customers)

        # Expand this object to a tree-like structure
        out = []
        for customer in customers:
            print(customer)
            print(customer.rel_orders)
            tmp = customer.to_dict()
            out.append(tmp)

        # print("Out length is: ", len(out))
        # print("Out length is: ", out[0])
        # print("Out length is: ", out)

        return out

    def read_customers_obj(self):
        customers = self.session.query(Customer).all()
        return customers

    def read_customers_by_customer_username(self, username):
        customer = self.session.query(Customer).filter(Customer.user_name == username).one_or_none()

        assert customer, (
        "We previously had checked if this customer exists. There is something wrong in the code", customer)

        print("Customer is: ", customer)
        # Expand this object to a tree-like structure
        print(customer)
        print(customer.rel_orders)

        return customer

    def read_parts(self):
        parts = self.session.query(Part).all()

        # print("Parts are: ", parts)

        # Expand this object to a tree-like structure
        out = []
        for part in parts:
            print(part)
            tmp = part.to_dict()
            out.append(tmp)

        print("Out length is: ", len(out))
        print("Out length is: ", out[:5])

        return out

    def read_part_by_part_id_obj(self, idx):
        part = self.session.query(Part).filter(Part.id == idx).one_or_none()
        assert part, ("We previously had checked if this part exists. There is something wrong in the code", part)
        return part

    def read_part_by_part_external_identifier_obj(self, external_identifier):
        part = self.session.query(Part).filter(Part.part_external_identifier == external_identifier).one_or_none()
        assert part, ("We previously had checked if this part exists. There is something wrong in the code", part)
        return part

    ########################
    # UPDATE Operations
    ########################

    ########################
    # DELETE Operations
    ########################


screaper_database = Database()

if __name__ == "__main__":
    print("Starting to create databsse connection")
    database = Database()
    print("Successfully created and populated the database")
