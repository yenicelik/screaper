import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, false
from sqlalchemy.orm import Session, sessionmaker

import screaper
from screaper.resources.entities import Markup, UrlTaskQueue

load_dotenv()


class Database:
    """
        Wrapper to handle all I/O with the database.

        Implements basic CRUD operations

        Actually, let's not implement CRUD, but the actual operations that are used.
        The CRUD is already implemented by the ORM
    """

    def __init__(self):
        db_url = os.getenv('DatabaseUrl')
        self.engine = create_engine(db_url, encoding='utf8')

        # self.engine = screaper.resources.entities.engine
        Session = sessionmaker()
        Session.configure(bind=self.engine)
        self.session = Session()

        self.max_retries = 4
        self.engine_version = "0.0.1"

    def commit(self):
        self.session.commit()

    # Task queue
    def create_url_task_queue_record(
            self,
            target_url,
            referrer_url,
            skip
    ):
        obj = UrlTaskQueue(
            url=target_url,
            referrer_url=referrer_url,
            crawler_processing_sentinel=False,
            crawler_processed_sentinel=False,
            crawler_skip=skip,
            engine_version=self.engine_version
        )
        self.session.add(obj)

    def get_url_task_queue_record_start(self):
        """
            implements the pop operation for queue,
            retrieving the next item to work on.

            Return a success boolean
        """
        # Get the one inserted most recently
        obj = self.session.query(UrlTaskQueue)\
            .filter(UrlTaskQueue.crawler_skip == false())\
            .order_by(UrlTaskQueue.created_at)\
            .limit(1)\
            .one_or_none()
        # throw some exception that the queue is empty!
        # (in this case, just restart the program or so, throwing an execption is fine)
        obj.crawler_processing_sentinel = True
        return obj

    def get_url_task_queue_record_completed(self, url):
        """
            implements part of the pop operation for queue,
            indicating that a crawler has processed the request successfully
        """
        obj = UrlTaskQueue(url=url)
        # self.session.query(obj).update({"crawler_processed_sentinel": True})
        obj.crawler_processed_sentinel = True
        return obj

    def get_url_task_queue_record_failed(self, url):
        """
            implements the pop operation for queue
            indicating that a crawler has processed the request successfully
        """
        obj = UrlTaskQueue(url=url)
        # If retried too many times and failed, skip
        skip = obj.retries + 1 >= self.max_retries
        # self.session.query(obj).update({
        #     "crawler_processing_sentinel": False,
        #     "skip": skip,
        #     "retries": obj.retries + 1
        # })
        obj.crawler_processed_sentinel = False
        obj.skip = skip
        obj.retries += 1
        return obj

    # Markup
    def create_markup_record(
            self,
            url,
            referrer_url,
            markup,
            skip
    ):
        # generate a random 64-bit random string
        obj = Markup(
            url=url,
            referrer_url=referrer_url,
            markup=markup,
            spider_processing_sentinel=False,
            spider_processed_sentinel=False,
            spider_skip=skip,
            engine_version=self.engine_version
        )
        self.session.add(obj)

    def get_markup_exists(
            self,
            url
    ):
        # Can also make this conditional on a timeout variable
        result = self.session.query(Markup).filter(Markup.url == url).one_or_none()
        out = True if result else False
        return out



resource_database = Database()

if __name__ == "__main__":
    print("Handle all I/O")
