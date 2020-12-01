"""
    Implements all models to be implemented by the postgres database. This includes
    - The scraped files
    - The task queue
"""
import uuid

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Text, Boolean, PrimaryKeyConstraint
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from sqlalchemy_utils import URLType

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class UrlTaskQueue(Base):
    """
        The URLTypeask queue
    """

    __tablename__ = 'url_task_queue'

    url = Column(URLType, primary_key=True, unique=True, nullable=False)  # Make this an index
    referrer_url = Column(URLType, primary_key=True, nullable=False)

    queue_uri = Column(String(length=64), unique=True, nullable=False, default=generate_uuid)  # Create a random 64-char hash as a unique identifier
    crawler_processing_sentinel = Column(Boolean(), nullable=False)  # Indicates if a worker is currently processing this
    crawler_processed_sentinel = Column(Boolean(), nullable=False)  # Indicates if the URLTypeas been successfully crawled
    crawler_skip = Column(Boolean(), nullable=False)  # Indicates whether or not to skip scraping this website
    retries = Column(Integer(), nullable=False, default=0)  # Indicates the version under which the link was scraped for
    occurrences = Column(Integer(), nullable=False, default=0)  # Indicates how often this link was found, s.t. a priority queue can be managed through this
    engine_version = Column(String(), nullable=False)  # Indicates the version under which the link was scraped for

    id = Column(Integer(), autoincrement=True, nullable=False, default=0)
    created_at = Column(DateTime(), default=datetime.utcnow(), nullable=False)  # Timestamp when the query is added to the queue

    __table_args__ = (
        PrimaryKeyConstraint('url', 'referrer_url'),
        {},
    )

# TODO: You will then this markup, and start reshaping this into a processed form
class Markup(Base):
    """
        The index which aggregates all website data.
        We assume that the url markup is independent of the referrer_url.
    """

    __tablename__ = 'markup'

    url = Column(URLType, primary_key=True, unique=True, nullable=False)  # Make this an index

    index_uri = Column(String(length=64), unique=True, default=generate_uuid, nullable=False)  # Create a random 64-char hash as a unique identifier
    markup = Column(Text(), nullable=False)
    spider_processing_sentinel = Column(Boolean(), nullable=False)  # Indicates if a spider worker is currently processing this
    spider_processed_sentinel = Column(Boolean(), nullable=False)  # Indicates if a spider worker has been successfully processed
    spider_skip = Column(Boolean(), nullable=False)  # Indicates if a spider worker has been successfully processed
    engine_version = Column(String(), nullable=False)  # Indicates the version under which the link was scraped for

    id = Column(Integer(), autoincrement=True, nullable=False, default=0)
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
