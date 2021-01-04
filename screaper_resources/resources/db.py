import os
import random
import time

import sqlalchemy
import yaml

import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, false, func, update
from sqlalchemy.orm import sessionmaker

from screaper_resources.resources.entities import URLQueueEntity, URLEntity, URLReferralsEntity, RawMarkup, \
    NamedEntities

load_dotenv()

# TODO: Add query normalization

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

    def create_url_entity(self, urls):
        existing_urls = self.session.query(URLEntity.url).filter(URLEntity.id.in_(urls)).all()
        missing_urls = [x for x in urls if x not in existing_urls]

        # Create a new URL object
        to_insert = []
        for url in missing_urls:
            url_entity_obj = URLEntity(
                url=url,
                engine_version=self.engine_version
            )
            to_insert.append(url_entity_obj)

        # Apply a bulk insert
        self.session.bulk_save_objects(to_insert)

    # Perhaps a bulk operation instead?
    # TODO: Make this to a bulk query
    # TODO: Change this to a url entity
    def create_url_queue_entity(self, url_skip_tuples):
        """
            Assumes that the URL was already input into the URL queue!!
        :param urls:
        :param skip:
        :return:
        """
        urls = [x[0] for x in url_skip_tuples]
        skip_flags = [x[1] for x in url_skip_tuples]

        # Check which URLs were already submitted
        url_ids = self.session.query(URLEntity.id)\
            .filter(URLEntity.id.in_(urls)).all()

        assert len(url_ids) == len(urls), ("Not same size!", url_ids, urls)

        # Increment occurrences count for existing url_queue_objects
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id)\
            .filter(URLEntity.url.in_(url_ids))
        query.update({URLQueueEntity.occurrences: URLQueueEntity.occurrences + 1}, synchronize_session=False)

        # Create queue objects for non-existing url_queue_objects
        # Create URL objects for all urls that were not included already
        to_insert = []
        for url_id, skip_flag in zip(url_ids, skip_flags):
            # Add to the queue if not already within the queue
            url_queue_obj = URLQueueEntity(
                url_id=url_id,
                crawler_processing_sentinel=False,
                crawler_processed_sentinel=False,
                crawler_skip=skip_flag,
                version_crawl_frontier=self.engine_version
            )
            to_insert.append(url_queue_obj)

        self.session.add(to_insert)

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

    #####################################################
    #                                                   #
    #   Bulk, expensive, often-time, often-called ops   #
    #                                                   #
    #####################################################

    # Write bulk operation instead?
    def get_url_task_queue_record_start_list(self):
        """
            Retrieve a list of URL sites to retrieve
        :return:
        """

        # TODO: Make it mixed,
        # such that there is a limit of how many urls from one domain can be picked

        start_time = time.time()
        # Get the one inserted most recently,
        # which is not processing
        # and is not included in the index already

        # .filter(URLQueueEntity.crawler_skip == false()) \

        # TODO: Prebuild queries ?

        # filter out any sites which are over-proportionally visited
        # .filter(sqlalchemy.and_(*self.popular_websites_filter_query))

        # .filter(sqlalchemy.not_(URLEntity.url.contains('tel://'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('javascript'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('doi.org'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('wikimedia.org'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('news'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('microsoft'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('wiki'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('ftp:'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('help'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('media'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('.hp.com'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('google'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('archive'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('.se.com'))) \
        # .filter(sqlalchemy.not_(URLEntity.url.contains('go4worldbusiness.com'))) \

        # .join(RawMarkup, isouter=True) \
        # .filter(RawMarkup.id == None) \

            # Make sure markup does not exist yet?s
        # TODO: Implement priority logic into this function.
        # Doesnt make much sense to retrieve and set a sentinel for this, I think
        # Also include that markup should not be included
        query_list = self.session.query(URLEntity.url, URLQueueEntity.id) \
            .join(RawMarkup, isouter=True) \
            .filter(RawMarkup.id == None) \
            .filter(URLQueueEntity.crawler_processing_sentinel == false()) \
            .filter(URLQueueEntity.retries < self.max_retries) \
            .filter(URLEntity.id == URLQueueEntity.url_id) \
            .filter(
                sqlalchemy.or_(
                    URLEntity.url.contains('thomasnet.com'),
                    URLEntity.url.contains('go4worldbusiness.com')
                )
            ) \
            .order_by(
            # URLQueueEntity.occurrences.desc(),
            # URLQueueEntity.created_at.asc()
            func.random()
            # Gotta do random takeout as we use multiprocessing
        ).limit(512).all()

        # TODO: Possibility to yield

        # TODO: Make sure the ids don't exist in the markup table yet!

        print("Query list is: ", query_list)
        # Python unzip function?
        queue_uris = [x[0] for x in query_list]
        queue_uri_ids = [x[1] for x in query_list]

        print("Getting queue (1) takes {:.3f} seconds".format(time.time() - start_time))

        # Bulk update
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.id.in_(queue_uri_ids))
        query.update({"crawler_processing_sentinel": True}, synchronize_session=False)

        print("Getting queue (2) takes {:.3f} seconds".format(time.time() - start_time))

        return queue_uris

    def get_url_task_queue_record_completed(self, urls):
        """
            implements part of the pop operation for queue,
            indicating that a crawler has processed the request successfully
        """
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id).filter(URLEntity.url.in_(urls))
        query.update({"crawler_processed_sentinel": True}, synchronize_session=False)

    def get_url_task_queue_record_failed(self, urls):
        """
            implements the pop operation for queue
            indicating that a crawler has processed the request successfully
        """

        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id).filter(URLEntity.url.in_(urls))
        query.update(
            values={
                URLQueueEntity.retries: URLQueueEntity.retries + 1,
                URLQueueEntity.crawler_processed_sentinel: False,
                URLQueueEntity.crawler_processing_sentinel: False,
                URLQueueEntity.crawler_skip: URLQueueEntity.retries + 1 >= self.max_retries,
            },
            synchronize_session=False
        )

    def create_markup_record(self, url_markup_tuple_dict):
        """
        :param url_markup_tuple_dict: Dictionary of url -> markup
        """
        urls = [x for x in url_markup_tuple_dict.keys()]

        query = self.session.query(URLEntity.id, URLEntity.url, RawMarkup.id) \
            .filter(URLEntity.url.in_(urls)) \
            .join(RawMarkup, isouter=True) \
            .all()

        # TODO: Must be an outer join!

        to_insert = []
        for obj in query:
            url_id, url, markup_id = obj
            print("Looking at: ", url_id, markup_id, url)
            # If existent, just create a new entry. The timestamps will differentiate anyways
            obj = RawMarkup(
                url_id=url_id,
                markup=url_markup_tuple_dict[url],
                spider_processing_sentinel=False,
                spider_processed_sentinel=False,
                spider_skip=False,
                version_spider=self.engine_version
            )
            to_insert.append(obj)

        print("Bulk inserting", len(to_insert))
        # Bulk save all the markups that were fetched

        # sqlalchemy.exc.IntegrityError: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "raw_markup_pkey"
        # DETAIL:  Key (id)=(3540) already exists.

        self.session.bulk_save_objects(to_insert)

        # Do not update anything to processed, this will be done in one of the next steps anyways

    #####################################################
    #                                                   #
    # Non-bulk, cheap, one-time, few-called operations  #
    #                                                   #
    #####################################################
    def get_number_of_queued_urls(self):
        result = self.session.query(URLQueueEntity).count()
        return result

    def get_number_of_crawled_sites(self):
        result = self.session.query(RawMarkup).count()
        return result

    def get_all_indexed_markups(self, dev=False):
        with self.engine.connect() as connection:
            query_result = connection.execute(
                "SELECT url, markup, raw_markup.id AS markup_id FROM url, raw_markup WHERE url.id = raw_markup.url_id {};".format(
                    "ORDER BY RANDOM() LIMIT 16" if dev else ""))
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

    database = Database()
    database.get_url_task_queue_record_start_list()
