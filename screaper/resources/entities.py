"""
    Implements all models to be implemented by the postgres database. This includes
    - The scraped files
    - The task queue
"""
import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Text, Boolean
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from dotenv import load_dotenv
from sqlalchemy_utils import URLType

Base = declarative_base()

load_dotenv()

db_url = os.getenv('DatabaseUrl')
engine = create_engine(db_url, encoding='utf8')

# set default utf-8

class UrlTaskQueue(Base):
    """
        The URLTypeask queue
    """

    __tablename__ = 'url_task_queue'


    queue_uri = Column(String(length=64), unique=True)  # Create a random 64-char hash as a unique identifier
    url = Column(URLType, primary_key=True)  # Make this an index
    referrer_url = Column(URLType)
    crawler_processing_sentinel = Column(Boolean())  # Indicates if a worker is currently processing this
    crawler_processed_sentinel = Column(Boolean())  # Indicates if the URLTypeas been successfully crawled
    crawler_skip = Column(Boolean())  # Indicates whether or not to skip scraping this website
    engine_version = Column(String())  # Indicates the version under which the link was scraped for

    id = Column(Integer(), primary_key=True, autoincrement=True)
    created_at = Column(DateTime(), default=datetime.utcnow())  # Timestamp when the query is added to the queue


class Markup(Base):
    """
        The index which aggregates all website data
    """

    __tablename__ = 'markup'

    index_uri = Column(String(length=64), unique=True)  # Create a random 64-char hash as a unique identifier
    url = Column(URLType, primary_key=True)  # Make this an index
    referrer_url = Column(URLType)
    markup = Column(Text())
    spider_processing_sentinel = Column(Boolean())  # Indicates if a spider worker is currently processing this
    spider_processed_sentinel = Column(Boolean())  # Indicates if a spider worker has been successfully processed
    spider_skip = Column(Boolean())  # Indicates if a spider worker has been successfully processed

    id = Column(Integer(), primary_key=True, autoincrement=True)
    updated_at = Column(DateTime(), default=datetime.utcnow())


if __name__ == "__main__":
    print("Model files")

    # create all tables
    Base.metadata.create_all(engine)



