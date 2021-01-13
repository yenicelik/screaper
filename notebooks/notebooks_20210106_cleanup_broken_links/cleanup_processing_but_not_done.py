"""
    Clearn up tasks that are processing, but are not done for some reason (thread prob broke)
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, true, false
from sqlalchemy.orm import scoped_session, sessionmaker

from screaper_resources.resources.entities import URLQueueEntity

load_dotenv()

db_url = os.getenv("DatabaseUrl")
engine = create_engine(db_url, encoding='utf8', pool_size=5, max_overflow=10)  # pool_timeout=1

Session = scoped_session(sessionmaker(autocommit=False, autoflush=True, expire_on_commit=False, bind=engine))
session = Session()

def clean_processing_but_not_processsed():
    query = session.query(URLQueueEntity)\
        .filter(URLQueueEntity.crawler_processing_sentinel == true())\
        .filter(URLQueueEntity.crawler_processed_sentinel == false())
    query.update({URLQueueEntity.crawler_processing_sentinel: false()}, synchronize_session=False)
    print("Processed {} rows".format(query.count()))
    session.commit()

def remove_duplicate_markups():
    """
    DELETE FROM raw_markup
    WHERE id IN(SELECT id FROM(SELECT  id, ROW_NUMBER() OVER(PARTITION BY url_id ORDER BY id)
    AS row_num FROM raw_markup) t WHERE t.row_num > 1);
    :return:
    """
    # Create a unique index (each link only has one markup saved)

if __name__ == "__main__":
    print("Cleaning data a bit more because of broke threads etc.")
    clean_processing_but_not_processsed()
