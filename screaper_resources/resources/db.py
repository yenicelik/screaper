import os
import time
import random

import sqlalchemy

import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, false
from sqlalchemy.orm import sessionmaker, scoped_session

from screaper.crawl_frontier.crawl_frontier import CrawlObject
from screaper_resources.resources.entities import URLQueueEntity, URLEntity, URLReferralsEntity, RawMarkup, \
    NamedEntities, ActorEntityCandidates

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

        ############################################
        #
        #   Check which URLs were already created
        #
        ############################################        urls = set(urls)
        existing_urls = self.session.query(URLEntity.url).filter(URLEntity.url.in_(urls)).all()
        existing_urls = [x[0] for x in existing_urls]
        print("Existent urls: ", existing_urls)
        # print("Existing urls are: ", existing_urls)
        missing_urls = [x for x in urls if x not in existing_urls]
        # print("Missing urls are: ", missing_urls)
        assert len(set(missing_urls)) == len(missing_urls), ("create URL entities not unique!", len(set(missing_urls)), len(missing_urls))

        ############################################
        #
        #   Create a new URL entity for the ones that don't exist yet
        #
        ############################################
        to_insert = []
        for url in missing_urls:
            url_entity_obj = URLEntity(
                url=url,
                engine_version=self.engine_version
            )
            print("Inserting urls: ", url)
            to_insert.append(url_entity_obj)

        # Apply a bulk insert
        self.session.bulk_save_objects(to_insert)

    def create_url_queue_entity(self, url_skip_score_depth_tuple_dict):
        """
            Assumes that the URL was already input into the URL queue!!
        """

        ############################################
        #
        #   Check which URLs were already created
        #
        ############################################

        print("URL skip score depth tuple is: ", url_skip_score_depth_tuple_dict)
        urls = list(set([x for x in url_skip_score_depth_tuple_dict.keys()]))
        urls_id_url_tuples = self.session.query(URLEntity.id, URLEntity.url).filter(URLEntity.url.in_(urls)).all()
        assert len(urls_id_url_tuples) == len(url_skip_score_depth_tuple_dict), ("You must first insert a URL before you can add it to the queue!", len(urls_id_url_tuples), len(url_skip_score_depth_tuple_dict))

        ############################################
        #
        #   Check which URLs were already inputted to the queue and which ones were not
        #
        ############################################
        queued_urls = self.session.query(URLEntity.url) \
            .filter(URLEntity.id == URLQueueEntity.url_id) \
            .filter(URLEntity.url.in_(urls)).all()

        existent_queue_elements = [x for x in urls_id_url_tuples if x[1] in queued_urls]
        to_be_inserted_queue_elements = [x for x in urls_id_url_tuples if x[1] not in queued_urls]
        assert len(existent_queue_elements) + len(to_be_inserted_queue_elements) == len(set(urls)), ("Mismatch in the number of URLs to be inputted!", len(existent_queue_elements), len(to_be_inserted_queue_elements), len(set(urls)))

        ############################################
        #
        #   For the urls that are already in the queue, increment the occurrences counter
        #
        ############################################
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id) \
            .filter(URLEntity.id.in_([x[0] for x in existent_queue_elements]))
        query.update({URLQueueEntity.occurrences: URLQueueEntity.occurrences + 1}, synchronize_session=False)

        ############################################
        #
        #   For the urls that are not in the queue, insert it into the queue
        #
        ############################################
        to_insert = []
        for url_id, queue_url in to_be_inserted_queue_elements:
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

        ############################################
        #
        #   Check which URLs were already created
        #
        ############################################

        target_urls = [x[0] for x in target_url_referrer_url_tuple_list]
        referrer_urls = [x[1] for x in target_url_referrer_url_tuple_list]

        # Make sure target urls are entered as URLs
        # Retrieve the URL ids. These must already have been inserted!:
        target_url_ids = self.session.query(URLEntity.id).filter(URLEntity.url.in_(target_urls)).all()
        assert len(target_urls) == len(target_url_referrer_url_tuple_list), ("You must first insert a URL before you can add it to the queue!", len(target_url_referrer_url_tuple_list), len(target_urls))

        referrer_url_ids = self.session.query(URLEntity.id, URLEntity.url).filter(URLEntity.url.in_(referrer_urls)).all()
        assert len(referrer_urls) == len(target_url_referrer_url_tuple_list), ("You must first insert a URL before you can add it to the queue!", len(target_url_referrer_url_tuple_list), len(referrer_urls))

        ############################################
        #
        #   Check which referral pairs (target_url, original_url) are already input, and skip those
        #
        ############################################

        already_inserted_referral_pairs = self.session.query(URLReferralsEntity.target_url_id, URLReferralsEntity.referrer_url_id) \
            .filter(
            sqlalchemy.tuple_(URLReferralsEntity.target_url_id, URLReferralsEntity.referrer_url_id).in_(
                list(zip(target_url_ids, referrer_url_ids)))
        ).all()

        # Skip the ones that were already inserted
        originally_to_be_input_items = list(zip(target_url_ids, referrer_url_ids))
        target_url_id_referrer_url_id_tuple_list = [x for x in originally_to_be_input_items if x not in already_inserted_referral_pairs]
        assert len(target_url_id_referrer_url_id_tuple_list) <= len(originally_to_be_input_items), ("You should have received less items after checking if an item was inserted already!", len(target_url_id_referrer_url_id_tuple_list), len(originally_to_be_input_items))

        ############################################
        #
        #   For the url-pairs that are not in the adjacency graph, insert it
        #
        ############################################
        # Create and insert the referral pair
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
            Retrieve a list of URL sites to scrape next
            # TODO: Make it mixed, such that there is a limit of how many urls from one domain can be picked
            # TODO: Prebuild queries ?
        :return:
        """

        start_time = time.time()
        # Such that there is some sort of non-overlap mechanism across processes
        random_prime = random.choice([1, 2, 3, 5, 7, 11, 13, 17, 19, 23, 29])

        raw_markup_items = self.session.query(RawMarkup.url_id)
        query_list = self.session.query(URLEntity.url, URLQueueEntity.id, URLQueueEntity.depth) \
            .filter(URLQueueEntity.crawler_skip == false()) \
            .filter(sqlalchemy.not_(URLQueueEntity.url_id.in_(raw_markup_items))) \
            .filter(URLQueueEntity.crawler_processing_sentinel == false()) \
            .filter(URLQueueEntity.retries < self.max_retries) \
            .filter(URLQueueEntity.depth != -1) \
            .filter(URLQueueEntity.id % random_prime == 0) \
            .order_by(URLQueueEntity.depth.asc()) \
            .limit(512)

        query_list = query_list.all()

        out = []
        for x in query_list:
            out.append(CrawlObject(url=x[0], queue_id=x[1], depth=x[2]))

        # Make sure no duplicate entries ...
        assert len([x.url for x in out]) == len(set([x.url for x in out])), ("Non-unique uris found!", len([x.url for x in out]), len(set([x.url for x in out])))

        print("Getting queue (1) takes {:.3f} seconds".format(time.time() - start_time))
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.id.in_([x.queue_id for x in out]))
        query.update({"crawler_processing_sentinel": True}, synchronize_session=False)
        print("Getting queue (2) takes {:.3f} seconds".format(time.time() - start_time))

        return out

    def get_url_task_queue_record_completed(self, urls):
        """
            implements part of the pop operation for queue,
            indicating that a crawler has processed the request successfully
        """
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id).filter(
            URLEntity.url.in_(urls))
        print("Number of items before processed: ", query.filter(URLQueueEntity.crawler_processed_sentinel == false()).count())
        query.update({"crawler_processed_sentinel": True}, synchronize_session=False)
        print("Number of items now processed: ", query.filter(URLQueueEntity.crawler_processed_sentinel == false()).count())


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
        c = 0
        for obj in query:
            url_id, url, markup_id = obj
            # If existent, just create a new entry. The timestamps will differentiate anyways
            if markup_id is not None:
                c += 1
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

        print("Bulk inserting raw_markup {} skipping {}".format(len(to_insert), c))
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

    def create_actor_entity_candidate(self, objs):
        for obj in objs:
            print("Inserting: ", obj)
            # Get URL id
            actor_entity_candidate = ActorEntityCandidates(**obj)
            self.session.add(actor_entity_candidate)

    def get_all_actor_entity_candidates(self):
        query = self.session.query(URLEntity.url, ActorEntityCandidates)\
            .filter(URLEntity.id == ActorEntityCandidates.url_id)\
            .limit(100)\
            .all()
        urls, actor_entity_candidates = [x[0] for x in query], [x[1] for x in query]
        return urls, actor_entity_candidates

if __name__ == "__main__":
    print("Handle all I/O")

    for i in range(10):
        start_time = time.time()

        database = Database()
        database.get_url_task_queue_record_start_list()
        database.commit()

        print("It takes this many seconds to retrieve the queue start: ", time.time() - start_time)
