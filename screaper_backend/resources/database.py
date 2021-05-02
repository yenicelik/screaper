"""
    Database
"""
import screaper_backend.scripts.database.initialize_db
import screaper_backend.scripts.database.initialize_mock
from screaper_backend.application import db
from screaper_backend.entities.entities_db import OrderItem, Order, Part, Customer, FileRecord


class Database:
    """
        Only CRUD functions should be implemented here
        Create
        Read
        Update
        Delete
    """

    def __init__(self, dev=False):
        # Create sqlalchemy database connection
        self.db = db

        # Create all tables (DEV)
        if dev:
            # TODO: Drop table completely
            self.db.create_all()

        self.session = self.db.session

        # Count number of items in the tables
        print("Count Order: ", self.session.query(Order).count())
        # print("Count Order: ", self.session.query(Order.id).all())
        print("Count OrderItem: ", self.session.query(OrderItem).count())
        # print("Count OrderItem: ", self.session.query(OrderItem.id).all())
        print("Count Parts: ", self.session.query(Part).count())
        # print("Count Parts: ", self.session.query(Part.id).all())
        print("Count Customers: ", self.session.query(Customer).count())
        # print("Count Customers (All): ", self.session.query(Customer.id).all())

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
            email=email,
            company_name=company_name,
            domain_name=domain_name,
            phone_number=phone_number,
            fax_number=fax_number,
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

    def create_order(self, customer, order, order_items, shipment_address,):

        assert order, order
        assert order_items, order_items

        order = self.create_single_order(
            customer=customer,
            reference=order.reference,
            shipment_address=shipment_address
        )
        for order_item in order_items:
            # TODO: Maybe retrieve part first
            part = self.read_part_by_part_id_obj(order_item.part_id)

            self.create_order_item(
                order=order,
                part=part,
                quantity=order_item.quantity,
                item_single_price=order_item.item_single_price,  #
            )

    def create_single_order(
            self,
            customer,
            reference,
            shipment_address,
            note=None
    ):
        # Make some type-tests, fail if not sufficient
        assert customer is not None, customer
        assert reference, reference

        if shipment_address is None:
            shipment_address = customer.address

        # owner=customer,
        order = Order(
            owner=customer,
            reference=reference,
            status="waiting_for_offer",
            shipment_address=shipment_address,
            note=note
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
            item_single_including_margin_price=None,
            cost_multiple=None
    ):
        # Make some type-tests, fail if not sufficient
        # save both the item single price, as well as the list price
        print("Entering new part into this now: ")
        # owner=order,
        # Put a default value on the final price
        if item_single_including_margin_price is None and cost_multiple is None:
            item_single_including_margin_price = 2.5 * part.manufacturer_price
        if cost_multiple:
            item_single_including_margin_price = cost_multiple * part.manufacturer_price
        order_item = OrderItem(
            order_id=order.id,
            rel_part=part,
            quantity=quantity,
            item_list_price=part.manufacturer_price,
            item_single_including_margin_price=item_single_including_margin_price,
        )
        print("New part is: ", order_item)
        self.session.add(order_item)
        self.session.commit()
        assert order_item.id, order_item.id
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

        # Expand this object to a tree-like structure
        # Only select top 50 orders
        # Also include to read all files associated to this order ...
        out = []
        for customer in customers:
            for order in customer.rel_orders:
                tmp1 = order.to_dict()
                tmp1["order_id"] = tmp1["id"]
                # print("tmp is: ")
                # print(tmp1)
                customer_dict = customer.to_dict()
                customer_dict["customer_id"] = customer_dict["id"]
                del customer_dict["id"]
                # TODO: The id in this should refer to the order_id
                tmp1.update(customer_dict)
                tmp1['items'] = []
                tmp1['files'] = []
                # print("tmp after is: ")
                # print(tmp1)
                for order_item in order.rel_order_items:
                    tmp2 = order_item.to_dict()
                    del tmp2['owner']
                    tmp2.update(order_item.rel_part.to_dict())
                    # Calculate the cost multiple
                    if (order_item.item_list_price):
                        tmp2['cost_multiple'] = order_item.item_single_including_margin_price / order_item.item_list_price
                    else:
                        # If the list price is zero, the item doesn't exist.
                        # put the listprice to negative, and then
                        tmp2['item_list_price'] = -1.
                        tmp2['cost_multiple'] = order_item.item_single_including_margin_price / -1.
                    # print("tmp 2 is: ", tmp2)
                    tmp1['items'].append(tmp2)
                    # print("Adding following object to the list (1):")
                    # print(tmp2)
                print("rel files are: ", order.rel_files)
                print(tmp1)
                for file_item in order.rel_files:
                    tmp2 = file_item.to_dict()
                    del tmp2['order_id']
                    del tmp2['id']
                    print("tmp 2 bfr is: ", tmp2['filename'])
                    # this has type of filestorage FileStorage(
                    # tmp2['file'] = b64encode(tmp2['file'])
                    print("tmp 2 is: ", tmp2['filename'])
                    tmp1['files'].append(tmp2)
                    # TODO: Generate a random ID
                    # print("Adding following object to the list (1):")
                # print("Adding following object to the list (2):")
                print("tmp1 files are: ", len(tmp1['files']))
                out.append(tmp1)

        print("Orders out are:")
        for order in out[:5]:
            print(order)

        out = out[:20]

        return out

    def read_orders_by_user(self, user_email):
        customers = self.session.query(Customer).filter(Customer.email == user_email).all()

        # Expand this object to a tree-like structure
        # Only select top 50 orders
        # Also include to read all files associated to this order ...
        out = []
        for customer in customers:
            for order in customer.rel_orders:
                tmp1 = order.to_dict()
                # print("tmp is: ")
                # print(tmp1)
                tmp1["order_id"] = tmp1["id"]
                tmp1.update(customer.to_dict())
                tmp1['items'] = []
                tmp1['files'] = []
                # print("tmp after is: ")
                # print(tmp1)
                for order_item in order.rel_order_items:
                    tmp2 = order_item.to_dict()
                    del tmp2['owner']
                    tmp2.update(order_item.rel_part.to_dict())
                    # print("tmp 2 is: ", tmp2)
                    tmp1['items'].append(tmp2)
                    # print("Adding following object to the list (1):")
                    # print(tmp2)
                print("rel files are: ", order.rel_files)
                print(tmp1)
                for file_item in order.rel_files:
                    tmp2 = file_item.to_dict()
                    del tmp2['order_id']
                    del tmp2['id']
                    print("tmp 2 bfr is: ", tmp2['filename'])
                    # this has type of filestorage FileStorage(
                    # tmp2['file'] = b64encode(tmp2['file'])
                    print("tmp 2 is: ", tmp2['filename'])
                    tmp1['files'].append(tmp2)
                    # TODO: Generate a random ID
                    # print("Adding following object to the list (1):")
                # print("Adding following object to the list (2):")
                print("tmp1 files are: ", len(tmp1['files']))
                out.append(tmp1)

        print("Orders out are:")
        for order in out[:5]:
            print(order)

        out = out[:20]

        return out

    def read_customers(self):
        customers = self.session.query(Customer).all()

        # Expand this object to a tree-like structure
        out = []
        for customer in customers:
            tmp = customer.to_dict()
            out.append(tmp)

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

    def read_customers_by_customer_email(self, email):
        customer = self.session.query(Customer).filter(Customer.email == email).one_or_none()
        assert customer, ("We previously had checked if this customer exists. There is something wrong in the code", customer)
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

    def read_order_exists_by_customer(self, order_id, customer_id):
        # First, get the
        print("Customer id is: ", order_id, customer_id)
        order = self.session.query(Order).filter(Order.customer_id == customer_id).filter(Order.id == order_id).one_or_none()
        assert order, (order, "Bad input!")
        # Gotta do some handling here!
        return order

    def read_order_exists_admin(self, order_id):
        # First, get the
        print("Order id is: ", order_id)
        order = self.session.query(Order).filter(Order.id == order_id).one_or_none()
        assert order, (order, "Bad input!")
        # Gotta do some handling here!
        return order

    ########################
    # UPDATE Operations
    ########################
    def update_single_order(
            self,
            old_order,
            tax_rate=None,
            absolute_discount=None,
            note=None,
            date_submitted=None,
            status=None,
            valid_through_date=None,
            expected_delivery_date=None,
            reference=None,
            shipment_address=None,
            paid_on_date=None,
            total_price_including_discount_and_taxrate=None,
            currency=None,
    ):
        # Make some type-tests, fail if not sufficient
        assert old_order is not None, old_order
        # order id must be provided, because this is an update operation!
        # we can safely ignore the customer to whom this belongs, also for the same reason
        # Ignore the order_id here lol, you already have received the actual object
        if tax_rate is not None:
            old_order.tax_rate = tax_rate
        if absolute_discount is not None:
            old_order.absolute_discount = absolute_discount
        if note is not None:
            old_order.note = note
        if date_submitted is not None:
            old_order.date_submitted = date_submitted
        if valid_through_date is not None:
            old_order.valid_through_date = valid_through_date
        if status is not None:
            old_order.status = status
        if expected_delivery_date is not None:
            old_order.expected_delivery_date = expected_delivery_date
        if reference is not None:
            old_order.reference = reference
        if shipment_address is not None:
            old_order.shipment_address = shipment_address
        if paid_on_date is not None:
            old_order.paid_on_date = paid_on_date
        if currency is not None:
            old_order.currency = currency
        if total_price_including_discount_and_taxrate is not None:
            old_order.total_price_including_discount_and_taxrate = total_price_including_discount_and_taxrate

        self.session.commit()
        print("Old order is: ", old_order)
        # self.session.refresh(old_order)
        # assert old_order.id
        return old_order

    ########################
    # DELETE Operations
    ########################
    def drop_order_items_for_order(
            self,
            order
    ):
        # Drop all such items
        # (I hope, this also deletes the backreference (?) )
        self.session.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
        self.session.commit()

    def drop_files_for_order(
            self,
            order
    ):
        # Drop all such items
        # (I hope, this also deletes the backreference (?) )
        self.session.query(FileRecord).filter(FileRecord.order_id == order.id).delete()
        self.session.commit()







screaper_database = Database()

if __name__ == "__main__":
    print("Starting to create databsse connection")
    database = Database()
    print("Successfully created and populated the database")
