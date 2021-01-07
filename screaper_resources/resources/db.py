import os
import time
import random

import sqlalchemy

import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, false, func, tablesample
from sqlalchemy.orm import sessionmaker, scoped_session, aliased

# from sqlalchemy.pool import NullPool
# poolclass=NullPool

from screaper_resources.resources.entities import URLQueueEntity, URLEntity, URLReferralsEntity, RawMarkup, \
    NamedEntities

load_dotenv()


# Perhaps try python 3.9?


# TODO: Add query normalization

# TODO: Replace all by the entity objects? probably better to operate with enums anyways
class Database:
    """
        Wrapper to handle all I/O with the database.

        Implements basic CRUD operations

        Actually, let's not implement CRUD, but the actual operations that are used.
        The CRUD is already implemented by the ORM
    """

    # For session placement, check code examples here:
    # https://docs.sqlalchemy.org/en/13/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it

    def __init__(self):
        db_url = os.getenv('DatabaseUrl')
        self.engine = create_engine(db_url, encoding='utf8', pool_size=5, max_overflow=10)  # pool_timeout=1

        # self.engine = screaper.resources.entities.engine
        Session = scoped_session(
            sessionmaker(autocommit=False, autoflush=True, expire_on_commit=False, bind=self.engine))
        # Session.configure()
        self.session = Session()

        self.max_retries = 4
        self.engine_version = "0.0.1"

    def commit(self):
        self.session.commit()

    def create_url_entity(self, urls):

        # Weed-out duplicate urls
        urls = set(urls)
        existing_urls = self.session.query(URLEntity.url).filter(URLEntity.url.in_(urls)).all()
        existing_urls = [x[0] for x in existing_urls]
        # print("Existing urls are: ", existing_urls)
        missing_urls = [x for x in urls if x not in existing_urls]
        # print("Missing urls are: ", missing_urls)

        assert len(set(missing_urls)) == len(missing_urls), (
        "create URL entities not unique!", len(set(missing_urls)), len(missing_urls))

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
    def create_url_queue_entity(self, url_skip_score_depth_tuple_dict):
        """
            Assumes that the URL was already input into the URL queue!!
        """

        # TODO: Test this function?

        urls = [x for x in url_skip_score_depth_tuple_dict.keys()]

        # Check which URLs were already submitted
        query = self.session.query(URLEntity.id, URLEntity.url) \
            .filter(URLEntity.id == URLQueueEntity.url_id) \
            .filter(URLEntity.url.in_(urls)).all()

        queued_url_ids = [x[0] for x in query]
        queue_url_urls = [x[1] for x in query]

        existent_queue_elements = [x for x in zip(queued_url_ids, queue_url_urls) if x[1] in urls]
        to_be_inserted_queue_elements = [x for x in zip(queued_url_ids, queue_url_urls) if x[1] not in urls]

        # assert len(url_ids) == len(urls), ("Not same size!", len(url_ids), len(urls), url_ids, urls)

        # Increment occurrences count for existing url_queue_objects
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id) \
            .filter(URLEntity.id.in_([x[0] for x in existent_queue_elements]))
        query.update({URLQueueEntity.occurrences: URLQueueEntity.occurrences + 1}, synchronize_session=False)

        # Filter out url_ids which were already input

        # Create queue objects for non-existing url_queue_objects
        # Create URL objects for all urls that were not included already
        to_insert = []
        for url_id, queue_url in to_be_inserted_queue_elements:
            # Add to the queue if not already within the queue
            url_queue_obj = URLQueueEntity(
                url_id=url_id,
                crawler_processing_sentinel=False,
                crawler_processed_sentinel=False,
                crawler_skip=url_skip_score_depth_tuple_dict[queue_url][0],
                version_crawl_frontier=self.engine_version,
                score=url_skip_score_depth_tuple_dict[queue_url][1],
                depth=url_skip_score_depth_tuple_dict[queue_url][2]
            )
            to_insert.append(url_queue_obj)

        self.session.bulk_save_objects(to_insert)

    def create_referral_entity(self, target_url_referrer_url_tuple_list):

        target_urls = [x[0] for x in target_url_referrer_url_tuple_list]
        referrer_urls = [x[1] for x in target_url_referrer_url_tuple_list]

        query = self.session.query(URLEntity.id, URLEntity.url).filter(URLEntity.url.in_(target_urls)).all()
        target_url_ids = [x[0] for x in query]
        target_urls = [x[1] for x in query]
        query = self.session.query(URLEntity.id, URLEntity.url).filter(URLEntity.url.in_(referrer_urls)).all()
        referrer_url_ids = [x[0] for x in query]
        referrer_urls = [x[1] for x in query]

        # Skip items that were already added
        # Just update items that were already added (this has low repercussions, also duplicates here just enforce the graph, which is fine)
        query = self.session.query(URLReferralsEntity.target_url_id, URLReferralsEntity.referrer_url_id) \
            .filter(
            sqlalchemy.tuple_(URLReferralsEntity.target_url_id, URLReferralsEntity.referrer_url_id).in_(
                list(zip(target_url_ids, referrer_url_ids)))
        ).all()

        # Filter out the items of
        # Remove all items that were already added
        originally_to_be_input_items = list(zip(target_url_ids, referrer_url_ids))
        target_url_id_referrer_url_id_tuple_list = [x for x in originally_to_be_input_items if x not in query]

        # Create the entity
        to_insert = []
        for x in target_url_id_referrer_url_id_tuple_list:
            target_url_id, referrer_url_id = x
            url_referral_entity_obj = URLReferralsEntity(
                target_url_id=target_url_id,
                referrer_url_id=referrer_url_id
            )
            to_insert.append(url_referral_entity_obj)

        self.session.bulk_save_objects(to_insert)

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

        # .order_by(
        #     URLQueueEntity.occurrences.desc(),
        #     # URLQueueEntity.created_at.asc()
        #     # func.random()
        #     # Gotta do random takeout as we use multiprocessing
        # )\

        # Make sure markup does not exist yet?s
        # TODO: Implement priority logic into this function.
        # Doesnt make much sense to retrieve and set a sentinel for this, I think
        # Also include that markup should not be included

        # TODO: Don't forget to add these back up!!!

        # .join(RawMarkup, isouter=True) \
        # .filter(RawMarkup.id == None) \
        # .offset(random_offset) \
        # .filter(
        #     sqlalchemy.or_(
        #         URLEntity.url.contains('thomasnet.com'),
        #         URLEntity.url.contains('go4worldbusiness.com')
        #     )
        # ) \

        # .order_by(URLQueueEntity.depth.asc()) \

        # Pick one where the id is divisible by a prime number
        random_prime = random.choice(
            [1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101,
             103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199])
        # Some pseudo-randomness lol. We include 1 such that there is a chance that all items are chosen

        # Get all raw markup items
        raw_markup_items = self.session.query(RawMarkup.url_id)

        # TODO: Select random subquery and order by depth
        query_list = self.session.query(URLEntity.url, URLQueueEntity.id, URLQueueEntity.depth) \
            .filter(URLQueueEntity.crawler_skip == false()) \
            .filter(sqlalchemy.not_(URLQueueEntity.url_id.in_(raw_markup_items))) \
            .filter(URLQueueEntity.crawler_processing_sentinel == false()) \
            .filter(URLQueueEntity.retries < self.max_retries) \
            .filter(URLQueueEntity.depth != -1) \
            .filter(URLQueueEntity.id % random_prime == 0) \
            .order_by(URLQueueEntity.depth.asc()) \
            .limit(512)

        # Make sure no duplicate entries ...

        query_list = query_list.all()

        # TODO: Filter out markups that are not included

        # TODO: Possibility to yield

        # TODO: Make sure the ids don't exist in the markup table yet!

        # Python unzip function?
        queue_uris = [x[0] for x in query_list]
        queue_uri_ids = [x[1] for x in query_list]
        queue_uri_depths = [x[2] for x in query_list]

        print("Getting queue (1) takes {:.3f} seconds".format(time.time() - start_time))

        # Bulk update
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.id.in_(queue_uri_ids))
        query.update({"crawler_processing_sentinel": True}, synchronize_session=False)

        print("Getting queue (2) takes {:.3f} seconds".format(time.time() - start_time))

        return queue_uris, queue_uri_depths

    def get_url_task_queue_record_completed(self, urls):
        """
            implements part of the pop operation for queue,
            indicating that a crawler has processed the request successfully
        """
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id).filter(
            URLEntity.url.in_(urls))
        query.update({"crawler_processed_sentinel": True}, synchronize_session=False)

    def get_url_task_queue_record_failed(self, urls):
        """
            implements the pop operation for queue
            indicating that a crawler has processed the request successfully
        """

        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id).filter(
            URLEntity.url.in_(urls))
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
        print("URL Markup tuple dict is: ", len(url_markup_tuple_dict))
        urls = [x for x in url_markup_tuple_dict.keys()]

        query = self.session.query(URLEntity.id, URLEntity.url, RawMarkup.id) \
            .filter(URLEntity.url.in_(urls)) \
            .join(RawMarkup, isouter=True) \
            .all()

        to_insert = []
        for obj in query:
            url_id, url, markup_id = obj
            # If existent, just create a new entry. The timestamps will differentiate anyways
            if markup_id is not None:
                continue
            obj = RawMarkup(
                url_id=url_id,
                markup=url_markup_tuple_dict[url],
                spider_processing_sentinel=False,
                spider_processed_sentinel=False,
                spider_skip=False,
                version_spider=self.engine_version
            )
            to_insert.append(obj)

        assert len(to_insert) <= len(url_markup_tuple_dict), ("Lengths are weird!", len(to_insert), len(url_markup_tuple_dict))


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

    for i in range(10):
        start_time = time.time()

        database = Database()
        database.get_url_task_queue_record_start_list()
        database.commit()

        print("It takes this many seconds to retrieve the queue start: ", time.time() - start_time)
