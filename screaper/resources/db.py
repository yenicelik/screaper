import os
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, false, exists
from sqlalchemy.orm import sessionmaker

from screaper.resources.entities import URLEntity, URLReferralsEntity, URLQueueEntity, RawMarkup

load_dotenv()


# TODO: Replace all by the entity objects? probably better to operate with enums anyways
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

    def create_url_entity(
            self,
            url
    ):
        url_entity_obj = self.session.query(URLEntity) \
            .filter(URLEntity.url == url) \
            .one_or_none()

        # Add the URL Into the Queue
        if url_entity_obj is None:
            # Create a URL Object
            url_entity_obj = URLEntity(
                url=url,
                engine_version=self.engine_version
            )
            self.session.add(url_entity_obj)

        return url_entity_obj

    # TODO: Replace all ocurrences of urls with URL entities
    def create_url_queue_entity(
            self,
            url_entity_obj,
            skip
    ):
        url_queue_obj = self.session.query(URLQueueEntity) \
            .filter(URLQueueEntity.url_id == url_entity_obj.id) \
            .one_or_none()

        # Add to the queue if not already within the queue
        if url_queue_obj is None:
            url_queue_obj = URLQueueEntity(
                url_id=url_entity_obj.id,
                crawler_processing_sentinel=False,
                crawler_processed_sentinel=False,
                crawler_skip=skip,
                version_crawl_frontier=self.engine_version
            )
            self.session.add(url_queue_obj)
        else:
            url_queue_obj.occurrences += 1

        return url_queue_obj

    def create_referral_entity(
            self,
            url_entity,
            referrer_url
    ):

        referrer_url_entity_obj = self.session.query(URLEntity) \
            .filter(URLEntity.url == referrer_url) \
            .one_or_none()

        # Only for the target_url, check if this is already in the queue
        # The referrer_url should be scraped by definition
        url_referral_entity_obj = self.session.query(URLReferralsEntity)\
            .filter(
                URLReferralsEntity.target_url_id == url_entity.id,
                URLReferralsEntity.referrer_url_id == referrer_url_entity_obj.id
            )\
            .one_or_none()

        # Add to the graph if not already within the graph
        if url_referral_entity_obj is None:
            url_referral_entity_obj = URLReferralsEntity(
                target_url_id=url_entity.id,
                referrer_url_id=referrer_url_entity_obj.id
            )
            self.session.add(url_referral_entity_obj)


    def get_url_task_queue_record_start(self):
        """
            implements the pop operation for queue,
            retrieving the next item to work on.

            Return a success boolean
        """
        # Get the one inserted most recently,
        # which is not processing
        # and is not included in the index already

        obj = self.session.query(URLQueueEntity)\
            .filter(URLQueueEntity.crawler_processing_sentinel == false())\
            .filter(URLQueueEntity.crawler_skip == false())\
            .filter(URLQueueEntity.retries < self.max_retries)\
            .order_by(
                URLQueueEntity.occurrences.asc(),
                URLQueueEntity.created_at.asc()
            )\
            .limit(1)\
            .join(URLEntity)\
            .one_or_none()

        obj.crawler_processing_sentinel = True

        return obj


    def get_url_task_queue_record_completed(self, url):
        """
            implements part of the pop operation for queue,
            indicating that a crawler has processed the request successfully
        """
        obj = self.session.query(URLEntity)\
            .filter(URLEntity.url == url)\
            .join(URLQueueEntity)\
            .first()

        # TODO: Will this update the sub-object in the database? (because join?)
        obj.crawler_processed_sentinel = True
        assert obj.crawler_processed_sentinel, obj.crawler_processed_sentinel
        return obj


    def get_url_task_queue_record_failed(self, url):
        """
            implements the pop operation for queue
            indicating that a crawler has processed the request successfully
        """
        obj = self.session.query(URLEntity)\
            .filter(URLEntity.url == url)\
            .join(URLQueueEntity)\
            .one()

        # TODO: Will this update the sub-object in the database? (because join?)
        # If retried too many times and failed, skip
        skip = obj.retries + 1 >= self.max_retries
        obj.crawler_processing_sentinel = False
        obj.crawler_processed_sentinel = False
        obj.skip = skip
        obj.retries += 1
        return obj

    # Markup
    def create_markup_record(
            self,
            url,
            markup
    ):
        url_entity = self.session.query(URLEntity)\
            .filter(URLEntity.url == url)\
            .one_or_none()

        # generate a random 64-bit random string
        obj = RawMarkup(
            url_id=url_entity.id,
            markup=markup,
            spider_processing_sentinel=False,
            spider_processed_sentinel=False,
            spider_skip=False,
            version_spider=self.engine_version
        )
        self.session.add(obj)

    def get_url_exists(self, url):
        url_entity = self.session.query(URLEntity)\
            .filter(URLEntity.url == url)\
            .one_or_none()

        return url_entity

    def get_number_of_crawled_sites(self):
        result = self.session.query(RawMarkup).count()
        return result

    def get_all_indexed_documents(self):
        with self.engine.connect() as connection:
            query_result = connection.execute("SELECT * FROM raw_markup;")
            column_names = query_result.keys()
            query_result = query_result.fetchall()

        print("Query result:", query_result)
        print("Column names: ", column_names)

        df = pd.DataFrame(query_result, columns=column_names)
        return df

resource_database = Database()

if __name__ == "__main__":
    print("Handle all I/O")
