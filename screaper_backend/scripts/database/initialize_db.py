"""
    Script to initialize the database, and load some custom data inside
"""
from screaper_backend.entities.entities_db import Part, Customer
from screaper_backend.importer.bmbaker_customers.data_importer_baker_customers import DataImporterBakerCustomers
from screaper_backend.importer.fischbein.data_importer_fischbein import DataImporterFischbein
from screaper_backend.importer.unionspecial.data_importer_unionspecial import DataImporterUnionSpecial
from screaper_backend.resources.database import screaper_database


def _populate_union_special_partslist_into_db(session):
    """
        Populates the database with the union special price list
    :return:
    """
    # Sort by external identifier (?) probably not needed ...
    data = DataImporterUnionSpecial().parts_list()
    # Only keep valid keys:
    # data = data.drop(columns=["searchstring"])
    # Push this into the table
    objs = []
    for obj in data.to_dict("records"):
        tmp = Part(**obj)
        objs.append(tmp)
    session.bulk_save_objects(objs)
    session.commit()

def _populate_fischbein_partslist_into_db(session):
    """
        Populates the database with the union special price list
    :return:
    """
    # Sort by external identifier (?) probably not needed ...
    data = DataImporterFischbein().parts_list()
    # Only keep valid keys:
    # data = data.drop(columns=["searchstring"])
    # Push this into the table
    objs = []
    for obj in data.to_dict("records"):
        tmp = Part(**obj)
        objs.append(tmp)
    session.bulk_save_objects(objs)
    session.commit()

def _populate_bmbaker_customerlist_into_db(session):
    """
        Populates the database with the union special price list
    :return:
    """
    # Sort by external identifier (?) probably not needed ...
    data = DataImporterBakerCustomers().customers_list()
    # Only keep valid keys:
    # data = data.drop(columns=["searchstring"])
    # Push this into the table
    objs = []
    for obj in data.to_dict("records"):
        tmp = Customer(**obj)
        objs.append(tmp)
    session.bulk_save_objects(objs)
    session.commit()

def _create_default_customers(database_wrapper):
    """
        Create some mock elements:
        - Create a single customer. This is the placeholder for all customers now
    :return:
    """
    # Create one "default" customer; which is used if no customer is defined
    database_wrapper.create_customer(
        user_name="default",
        company_name="No Customer Defined",
        phone_number="PHONE",
        fax_number="FAX",
        domain_name="DOMAIN",
        email="EMAIL",
        address="ADDRESS",
        city="CITY",
        country="COUNTRY",
        contact_name="CONTACT PERSON"
    )
    database_wrapper.session.commit()


def initialize_db():

    # Commit any tbd changes
    screaper_database.session.commit()
    # Drop all tables if existent
    screaper_database.db.drop_all()
    # Re-instantiate tables
    screaper_database.db.create_all()

    # Populate parts list
    _populate_union_special_partslist_into_db(screaper_database.session)
    _populate_fischbein_partslist_into_db(screaper_database.session)

    # Create default user
    _create_default_customers(screaper_database)

    # Create customer list
    _populate_bmbaker_customerlist_into_db(screaper_database.session)


if __name__ == "__main__":
    print("Initializing database...")
    initialize_db()
