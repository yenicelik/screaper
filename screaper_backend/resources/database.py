"""
    Database
"""
from sqlalchemy import create_engine, MetaData, update
from sqlalchemy.orm import sessionmaker

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
        self.create_single_order(customer_id=0, reference="ref MCY-GLS")
        self.create_order_item(
            product_id=5,
            quantity=50,
            price=50,
            origin="DE / US"
        )

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
        obj = Customer(
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
        self.session.add(obj)
        return obj

    def read_customer(self):
        customers = self.session.query(Customer).all()
        return customers

    def create_oder(self, order, order_items):

        assert order, order
        assert order_items, order_items

        self.create_single_order(order.customer_id, order.reference)
        for order_item in order_items:
            self.create_order_item(
                product_id=order_item.product_id,
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
        assert customer_id, customer_id
        assert reference, reference

        order = Order(
            customer_id=customer_id,
            reference=reference,
            status="offer created"
        )
        self.session.add(order)

    def create_order_item(
            self,
            product_id,
            quantity,
            price,
            origin
    ):
        # Make some type-tests, fail if not sufficient
        order_item = OrderItem(
            product_id=product_id,
            quantity=quantity,
            price=price,
            origin=origin
        )
        self.session.add(order_item)

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


if __name__ == "__main__":
    print("Starting to create databsse connection")
    database = Database()
    print("Successfully created and populated the database")
