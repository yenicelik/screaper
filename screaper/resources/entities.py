"""
    Implements all models to be implemented by the postgres database. This includes
    - The scraped files
    - The task queue
"""
import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Text, Boolean, PrimaryKeyConstraint, ForeignKey, Index
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from sqlalchemy_utils import URLType

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class URLEntity(Base):
    """
        The URL Class
    """
    __tablename__ = 'url'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False, default=0)
    url = Column(URLType, index=True, nullable=False)  # Make this an index

    occurrences = Column(Integer(), nullable=False, default=0)  # Indicates how often this link was found, s.t. a priority queue can be managed through this
    engine_version = Column(String(), nullable=False)  # Indicates the version under which the link was scraped for
    created_at = Column(DateTime(), default=datetime.utcnow(), nullable=False)  # Timestamp when the query is added to the queue


class URLQueueEntity(Base):
    """
        The URL Queue Class that the scraper is supposed to go through
    """
    __tablename__ = 'url_queue'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False, default=0)
    url = Column(Integer(), ForeignKey('url.id'), index=True, nullable=False)  # Make this an index
    crawler_processing_sentinel = Column(Boolean(), nullable=False)  # Indicates if a worker is currently processing this
    crawler_processed_sentinel = Column(Boolean(), nullable=False)  # Indicates if the URLTypeas been successfully crawled
    crawler_skip = Column(Boolean(), nullable=False)  # Indicates whether or not to skip scraping this website
    retries = Column(Integer(), nullable=False, default=0)  # Indicates the version under which the link was scraped for
    occurrences = Column(Integer(), nullable=False, default=0)  # Indicates how often this link was found, s.t. a priority queue can be managed through this
    created_at = Column(DateTime(), default=datetime.utcnow(), nullable=False)  # Timestamp when the query is added to the queue
    version_crawl_frontier = Column(String(), nullable=False)  # Indicates the version under which the link was scraped for


class URLReferralsEnttiy(Base):
    """
        The URL Queue Class that indicates what URL referred to what other URL
    """
    __tablename__ = 'url_referrals'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False, default=0)
    url = Column(Integer(), ForeignKey('url.id'), index=True, nullable=False)  # Make this an index
    referrer_url = Column(Integer(), ForeignKey('url.id'), primary_key=True, nullable=False)
    created_at = Column(DateTime(), default=datetime.utcnow(), nullable=False)  # Timestamp when the query is added to the queue

    __table_args__ = (
        Index('url', 'referrer_url'),
        {},
    )


class RawMarkup(Base):
    """
        The index which aggregates all website data.
        We assume that the url markup is independent of the referrer_url.
    """
    __tablename__ = 'raw_markup'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False, default=0)
    url = Column(Integer(), ForeignKey('url.id'), index=True, nullable=False)  # Make this an index
    markup = Column(Text(), nullable=False)
    version_crawl_processor = Column(String(), nullable=False)  # Indicates the version under which the link was scraped for
    updated_at = Column(DateTime(), default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)


class ProcessedMarkup(Base):
    """
        The index which includes the processed markups,
        and any information that arises from this
    """
    __tablename__ = 'processed_markup'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False, default=0)
    markup_id = Column(Integer(), ForeignKey('raw_markup.id'), index=True, nullable=False)  # Make this an index
    spider_processing_sentinel = Column(Boolean(), nullable=False)  # Indicates if a spider worker is currently processing this
    spider_processed_sentinel = Column(Boolean(), nullable=False)  # Indicates if a spider worker has been successfully processed
    spider_skip = Column(Boolean(), nullable=False)  # Indicates if a spider worker has been successfully processed
    version_spider = Column(String(), nullable=False)  # Indicates the version under which the link was scraped for
    updated_at = Column(DateTime(), default=datetime.utcnow(), onupdate=datetime.utcnow(), nullable=False)


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
