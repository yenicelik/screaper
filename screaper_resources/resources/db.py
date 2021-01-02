import os
import random
import sqlalchemy
import yaml

import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, false
from sqlalchemy.orm import sessionmaker

from screaper_resources.resources.entities import URLQueueEntity, URLEntity, URLReferralsEntity, RawMarkup, \
    NamedEntities

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

    def add_to_index(self, url, markup):
        """
            Adds a downloaded item to the markup
        """

        # For now, analyse any kind of markup
        self.create_markup_record(
            url=url,
            markup=markup
        )
        self.commit()

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
        url_referral_entity_obj = self.session.query(URLReferralsEntity) \
            .filter(
            URLReferralsEntity.target_url_id == url_entity.id,
            URLReferralsEntity.referrer_url_id == referrer_url_entity_obj.id
        ) \
            .one_or_none()

        # Add to the graph if not already within the graph
        if url_referral_entity_obj is None:
            url_referral_entity_obj = URLReferralsEntity(
                target_url_id=url_entity.id,
                referrer_url_id=referrer_url_entity_obj.id
            )
            self.session.add(url_referral_entity_obj)

        return url_referral_entity_obj

    def get_url_task_queue_record_start_list(self):
        """
            Retrieve a list of URL sites to retrieve
        :return:
        """
        # Get the one inserted most recently,
        # which is not processing
        # and is not included in the index already

        # .filter(URLQueueEntity.crawler_skip == false()) \

        # TODO: Prebuild queries ?

        # .filter(sqlalchemy.not_(URLEntity.url.contains('thomasnet.com'))) \
        # filter out any sites which are over-proportionally visited
        # .filter(sqlalchemy.and_(*self.popular_websites_filter_query))

        # TODO: Implement priority logic into this function.
        # Doesnt make much sense to retrieve and set a sentinel for this, I think
        query_list = self.session.query(URLEntity, URLQueueEntity) \
            .filter(URLQueueEntity.crawler_processing_sentinel == false()) \
            .filter(URLQueueEntity.retries < self.max_retries) \
            .filter(URLEntity.id == URLQueueEntity.url_id) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('tel://'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('javascript'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('doi.org'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('wikimedia.org'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('news'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('microsoft'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('wiki'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('ftp:'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('help'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('media'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('.hp.com'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('google'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('archive'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('.se.com'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('go4worldbusiness.com'))) \
            .join(URLEntity).order_by(
                URLQueueEntity.occurrences.desc(),
                # URLQueueEntity.created_at.asc()
                # func.random()
        ).limit(512).all()

        # TODO: make this a global variable on how many item to return to the queue?

        jobs = []
        for x in query_list:
            url_obj, url_queue_obj = x

            # Pick a random item from a list of 500 candidates
            jobs.append(url_obj)

            # Pick a pseudo-randomized order from the top 100 items
            url_queue_obj.crawler_processing_sentinel = True

        return jobs

    def get_url_task_queue_record_start(self):
        """
            implements the pop operation for queue,
            retrieving the next item to work on.

            Return a success boolean
        """
        # Get the one inserted most recently,
        # which is not processing
        # and is not included in the index already

        # .filter(URLQueueEntity.crawler_skip == false()) \

        # TODO: Prebuild queries ?

        # TODO: Implement priority logic into this function.
        # Doesnt make much sense to retrieve and set a sentinel for this, I think
        url_obj, url_queue_obj = random.choice(self.session.query(URLEntity, URLQueueEntity) \
            .filter(URLQueueEntity.crawler_processing_sentinel == false()) \
            .filter(URLQueueEntity.retries < self.max_retries) \
            .filter(URLEntity.id == URLQueueEntity.url_id) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('tel://'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('javascript'))) \
            # .filter(sqlalchemy.not_(URLEntity.url.contains('thomasnet.com'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('doi.org'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('wikimedia.org'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('news'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('microsoft'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('wiki'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('ftp:'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('help'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('media'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('.hp.com'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('google'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('archive'))) \
            .filter(sqlalchemy.not_(URLEntity.url.contains('.se.com'))) \
            # filter out any sites which are over-proportionally visited
            .filter(sqlalchemy.not_(URLEntity.url.contains('go4worldbusiness.com')))
            # .filter(sqlalchemy.and_(*self.popular_websites_filter_query))
            .join(URLEntity).order_by(
                URLQueueEntity.occurrences.desc(),
                # URLQueueEntity.created_at.asc()
                # func.random()
            ).limit(512).all())

        # Pick a random item from a list of 500 candidates

        # Pick a pseudo-randomized order from the top 100 items

        url_queue_obj.crawler_processing_sentinel = True

        return url_obj

    def get_url_task_queue_record_completed(self, url):
        """
            implements part of the pop operation for queue,
            indicating that a crawler has processed the request successfully
        """
        obj = self.session.query(URLEntity) \
            .filter(URLEntity.url == url) \
            .join(URLQueueEntity) \
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
        obj = self.session.query(URLQueueEntity) \
            .join(URLEntity) \
            .filter(URLEntity.url == url) \
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
        url_entity = self.session.query(URLEntity) \
            .filter(URLEntity.url == url) \
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
        url_entity = self.session.query(URLEntity) \
            .filter(URLEntity.url == url) \
            .one_or_none()

        return url_entity

    def get_markup_exists(self, url):
        url_entity = self.session.query(URLEntity) \
            .filter(URLEntity.url == url) \
            .join(RawMarkup) \
            .one_or_none()

        return url_entity

    def get_number_of_queued_urls(self):
        result = self.session.query(URLQueueEntity).count()
        return result

    def get_number_of_crawled_sites(self):
        result = self.session.query(RawMarkup).count()
        return result

    def get_all_indexed_markups(self, dev=False):
        with self.engine.connect() as connection:
            query_result = connection.execute("SELECT url, markup, raw_markup.id AS markup_id FROM url, raw_markup WHERE url.id = raw_markup.url_id {};".format("ORDER BY RANDOM() LIMIT 16" if dev else ""))
            column_names = query_result.keys()
            query_result = query_result.fetchall()

        print("Query result:", query_result)
        print("Column names: ", column_names)

        df = pd.DataFrame(query_result, columns=column_names)
        return df

    def add_named_entity_candidate(self, objs):
        for obj in objs:
            print("Inserting: ", obj)
            named_entity_obj = NamedEntities(**obj)
            self.session.add(named_entity_obj)

if __name__ == "__main__":
    print("Handle all I/O")
