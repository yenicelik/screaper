"""
    Implements all models to be implemented by the postgres database. This includes
    - The scraped files
    - The task queue
"""
import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Text, Boolean, PrimaryKeyConstraint, ForeignKey, Index, Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from sqlalchemy_utils import URLType

Base = declarative_base()


class URLEntity(Base):
    """
        The URL Class
    """
    __tablename__ = 'url'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)

    url = Column(URLType, unique=True, index=True)  # Make this an index
    engine_version = Column(String(), nullable=False)  # Indicates the version under which the link was scraped for

    created_at = Column(DateTime(), default=datetime.utcnow(),
                        nullable=False)  # Timestamp when the query is added to the queue


class URLQueueEntity(Base):
    """
        The URL Queue Class that the scraper is supposed to go through
    """
    __tablename__ = 'url_queue'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    url_id = Column(Integer(), ForeignKey('url.id'), unique=True, index=True, nullable=False)  # Make this an index
    crawler_processing_sentinel = Column(Boolean(),
                                         nullable=False)  # Indicates if a worker is currently processing this
    crawler_processed_sentinel = Column(Boolean(),
                                        nullable=False)  # Indicates if the URLTypeas been successfully crawled
    crawler_skip = Column(Boolean(), nullable=False)  # Indicates whether or not to skip scraping this website
    retries = Column(Integer(), nullable=False, default=0)  # Indicates the version under which the link was scraped for
    occurrences = Column(Integer(), nullable=False,
                         default=0)  # Indicates how often this link was found, s.t. a priority queue can be managed through this
    version_crawl_frontier = Column(String(),
                                    nullable=False)  # Indicates the version under which the link was scraped for
    score = Column(Integer(), nullable=False, default=0, index=True)

    created_at = Column(DateTime(), default=datetime.utcnow(),
                        nullable=False)  # Timestamp when the query is added to the queue


class URLReferralsEntity(Base):
    """
        The URL Queue Class that indicates what URL referred to what other URL
    """
    __tablename__ = 'url_referrals'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    target_url_id = Column(Integer(), ForeignKey('url.id'), index=True, nullable=False)  # Make this an index
    referrer_url_id = Column(Integer(), ForeignKey('url.id'), primary_key=True, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow(),
                        nullable=False)  # Timestamp when the query is added to the queue

    __table_args__ = (
        Index('target_url_id', 'referrer_url_id'),
        {},
    )


class RawMarkup(Base):
    """
        The index which aggregates all website data.
        We assume that the url markup is independent of the referrer_url.
    """
    __tablename__ = 'raw_markup'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    url_id = Column(Integer(), ForeignKey('url.id'), index=True, nullable=False)  # Make this an index
    markup = Column(Text(), nullable=False)
    spider_processing_sentinel = Column(Boolean(),
                                        nullable=False)  # Indicates if a spider worker is currently processing this
    spider_processed_sentinel = Column(Boolean(),
                                       nullable=False)  # Indicates if a spider worker has been successfully processed
    spider_skip = Column(Boolean(), nullable=False)  # Indicates if a spider worker has been successfully processed
    version_spider = Column(String(), nullable=False)  # Indicates the version under which the link was scraped for
    updated_at = Column(DateTime(), default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)


class ProcessedMarkup(Base):
    """
        The index which includes the processed markups,
        and any information that arises from this
    """
    __tablename__ = 'processed_markup'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    markup_id = Column(Integer(), ForeignKey('raw_markup.id'), index=True, nullable=False)  # Make this an index
    processed_markup = Column(Text(), nullable=False)
    updated_at = Column(DateTime(), default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)


class NamedEntities(Base):
    """
        The index of entities which includes
        (1) Companies
        (2) Products
    """

    __tablename__ = 'named_entities'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    markup_id = Column(Integer(), ForeignKey('raw_markup.id'), index=True, nullable=False)
    # location = Column(Integer(), nullable=False)  # Overkill for now, will have to manually search for this string
    entity_type = Column(
        Enum("PERSON", "NORP", "FACILITY", "ORGANIZATION", "GPE", "LOCATION", "PRODUCT", "EVENT", "WORK OF ART", "LAW",
             "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL", "OTHER", name="ner_types_enum"), nullable=False)
    label = Column(String(), nullable=False)
    external_link = Column(Integer(), ForeignKey('url.id'), nullable=True)
    heuristic = Column(String(), nullable=False)


if __name__ == "__main__":
    print("Model files")

    import os
    from sqlalchemy import Text, Boolean, create_engine
    from dotenv import load_dotenv

    load_dotenv()

    db_url = os.getenv('DatabaseUrl')
    engine = create_engine(db_url, encoding='utf8')
    # create all tables
    Base.metadata.create_all(engine)

    print("Done creating the tables")
