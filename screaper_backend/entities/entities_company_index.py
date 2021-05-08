"""
    Declares all database entities.
    This will likely match with front-end code
"""
import datetime
import enum

from sqlalchemy_serializer import SerializerMixin

from screaper_backend.application import db

################################
# Search Engine Entities
#################################
# Should probably not be a database object. Just do this, and save the finally extracted entities into a database table
# "EntityCandidates", which are then supposed to be double-checked by humans
class Company(db.Model, SerializerMixin):
    """
        The index of entities which includes

        (1) Companies
        (2) Products
    """

    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    company_name = db.Column(db.String(), nullable=False)
    company_slogan = db.Column(db.String(), nullable=False)
    description = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    label = db.Column(db.String, nullable=False)
    external_link = db.Column(db.URLType, nullable=True)
    external_phone = db.Column(db.String, nullable=True)

    # Connect this to what products they have
    #
    # secret_products_string =
    # trust score / neustahl_score -> should be determined by personal score -> should be determined by passive behavior and anonymous reviews
    # customer-satisfaction score
    # company certificates
