"""
    Implements all models to be implemented by the postgres database. This includes
    - The scraped files
    - The task queue
"""
from random import randint

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Text, Boolean, PrimaryKeyConstraint, ForeignKey, Enum, Index
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from sqlalchemy_utils import URLType

Base = declarative_base()


class URLRecord(Base):
    """
        The URL Class
    """
    __tablename__ = 'url'

    id = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime(), default=datetime.utcnow(), nullable=False)
    data = Column(URLType, unique=True, index=True)  # Make this an index
    status = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    retries = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    score = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)
    depth = Column(Integer(), primary_key=True, autoincrement=True, unique=True, nullable=False)


class URLReferralRecord(Base):
    """
        The URL Queue Class that indicates what URL referred to what other URL
    """
    __tablename__ = 'url_referral'

    referrer_id = Column(Integer(), ForeignKey('url.id'), index=True, nullable=False)  # Make this an index
    referee_id = Column(Integer(), ForeignKey('url.id'), index=True, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime(), default=datetime.utcnow(), nullable=False)
    count = Column(Integer(), nullable=False, default=1)

    __table_args__ = (
        (
            Index('target_url_id', 'referrer_url_id'),
        )
    )


class MarkupRecord(Base):
    """
        The index which aggregates all website data.
        We assume that the url markup is independent of the referrer_url.
    """
    __tablename__ = 'markup'

    url_id = Column(Integer(), ForeignKey('url.id'), primary_key=True, index=True, nullable=False)  # Make this an index
    created_at = Column(DateTime(), default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)
    updated_at = Column(DateTime(), default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)
    raw = Column(Text(), nullable=False)
    status = Column(Integer(), nullable=False)


# Should probably not be a database object. Just do this, and save the finally extracted entities into a database table
# "EntityCandidates", which are then supposed to be double-checked by humans
# class NamedEntities(Base):
#     """
#         The index of entities which includes
#         (1) Companies
#         (2) Products
#     """
#
#     __tablename__ = 'named_entities'
#
#     id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
#     markup_id = Column(Integer(), ForeignKey('raw_markup.id'), index=True, nullable=False)
#     # location = Column(Integer(), nullable=False)  # Overkill for now, will have to manually search for this string
#     entity_type = Column(
#         Enum("PERSON", "NORP", "FACILITY", "ORGANIZATION", "GPE", "LOCATION", "PRODUCT", "EVENT", "WORK OF ART", "LAW",
#              "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL", "OTHER",
#              name="ner_types_enum"), nullable=False)
#     label = Column(String(), nullable=False)
#     external_link = Column(Integer(), ForeignKey('url.id'), nullable=True)
#     heuristic = Column(String(), nullable=False)


# class ActorEntityCandidates(Base):
#     """
#         The index which includes potential Actors.
#         Actors can be one of (Supplier, Distributor, Manufacturer, Chamber of Commerce, Public Institution, Ministry, etc. ...)
#     """
#
#     __tablename__ = 'actor_entity_candidates'
#
#     url_id = Column(Integer(), ForeignKey('url.id'), primary_key=True, nullable=False)
#     title = Column(String(), nullable=False)
#     description = Column(String(), nullable=False)
#
#     # possible other items
#     # location
#     # neustahl_score -> should be determined by personal score
#
#     def as_dict(self):
#         return {c.name: getattr(self, c.name) for c in self.__table__.columns}


if __name__ == "__main__":
    print("Model files")

    import os
    from sqlalchemy import Text, Boolean, create_engine
    from dotenv import load_dotenv

    load_dotenv()

    # db_url = os.getenv('DatabaseUrl')
    # engine = create_engine(db_url, encoding='utf8')
    # create all tables
    # Base.metadata.create_all(engine)

    print("Done creating the tables")
