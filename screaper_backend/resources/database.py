"""
    Database
"""
import screaper_backend.scripts.database.initialize_db
import screaper_backend.scripts.database.initialize_mock
from screaper_backend.application import db
from screaper_backend.entities.entities_db import OrderItem, Order, Part, Customer, User, FileRecord


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

        # Create all tables (DEV)
        if dev:
            self.db.create_all()

        self.session = self.db.session

        # Count number of items in the tables
        print("Count Order: ", self.session.query(Order).count())
        print("Count Order: ", self.session.query(Order.id).all())
        print("Count OrderItem: ", self.session.query(OrderItem).count())
        print("Count OrderItem: ", self.session.query(OrderItem.id).all())
        print("Count Parts: ", self.session.query(Part).count())
        print("Count Parts: ", self.session.query(Part.id).all())
        print("Count Customers: ", self.session.query(Customer).count())
        print("Count Customers (All): ", self.session.query(Customer.id).all())

        # if the database connection string is a in-memory sqlalchemy one
        # then create the mock users
        if dev:
            # from screaper_backend.scripts.database.initialize_db import initialize_db
            # from screaper_backend.scripts.database.initialize_mock import _create_mock_customers, _create_mock_order

            screaper_backend.scripts.database.initialize_db.initialize_db(self)
            # screaper_backend.scripts.database.initialize_mock._create_mock_customers(self)
            screaper_backend.scripts.database.initialize_mock._create_mock_order(self)

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
            item_single_price
    ):
        # Make some type-tests, fail if not sufficient
        order_item = OrderItem(
            owner=order,
            rel_part=part,
            quantity=quantity,
            item_single_price=item_single_price
        )
        self.session.add(order_item)
        self.session.commit()
        self.session.refresh(order_item)
        assert order_item.id
        return order_item

    def create_file_item(
            self,
            order,
            file,
            filename
    ):
        # Make some type-tests, fail if not sufficient
        file_item = FileRecord(
            order=order,
            file=file,
            filename=filename
        )
        self.session.add(file_item)
        self.session.commit()
        self.session.refresh(file_item)
        assert file_item.id
        return file_item


    ########################
    # READ Operations
    ########################
    def read_orders(self):
        customers = self.session.query(Customer).all()

        print("Customers are: ", customers)

        # Expand this object to a tree-like structure
        # Only select top 50 orders
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

        print("Orders out are:")
        for order in out[:5]:
            print(order)

        out = out[:20]

        return out

    def read_user_obj(self, username):
        user = self.session.query(User).filter(User.username == username).one_or_none()

        return user

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
            tmp = part.to_dict()
            out.append(tmp)

        print("Out length is: ", len(out))
        for part in out[:5]:
            print("part is: ", part)

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
