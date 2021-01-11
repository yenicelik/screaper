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
    """

    # For session placement, check code examples here:
    # https://docs.sqlalchemy.org/en/13/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it

    def __init__(self):
        db_url = os.getenv('DatabaseUrl')
        self.engine = create_engine(db_url, encoding='utf8')  # pool_timeout=1 # pool_size=5, max_overflow=10

        # self.engine = screaper.resources.entities.engine
        Session = scoped_session(sessionmaker(autocommit=False, autoflush=True, expire_on_commit=False, bind=self.engine))
        # Session.configure()
        self.session = Session()

        self.max_retries = 4
        self.engine_version = "0.0.1"

    def commit(self):
        self.session.commit()

    def get_url_entity_not_inserted(self, urls):
        """
            Returns (1) a list of urls that are in the database, and (2) a list of urls that is not in the database
        """
        urls = list(set(urls))
        existing_urls = self.session.query(URLEntity.url).filter(URLEntity.url.in_(urls)).all()
        existing_urls = [x[0] for x in existing_urls]
        missing_urls = [x for x in urls if x not in existing_urls]
        assert len(set(missing_urls)) == len(missing_urls), ("create URL entities not unique!", len(set(missing_urls)), len(missing_urls))
        return missing_urls

    def insert_url_entity(self, urls):
        """
            Inserts the list of urls into the database
        """
        urls = list(set(urls))
        to_insert = []
        for url in urls:
            url_entity_obj = URLEntity(url=url, engine_version=self.engine_version)
            to_insert.append(url_entity_obj)

        # Apply a bulk insert
        self.session.bulk_save_objects(to_insert)

    def get_url_queue_inserted_and_missing(self, urls):
        """
            Returns (1) a list of urls that is enqueued, and (2) a list of urls that is not enqueued
            and still needs to be inserted into the queue
        """
        urls = list(set(urls))
        existing_urls = self.session.query(URLEntity.url)\
            .filter(URLEntity.url.in_(urls))\
            .filter(URLEntity.id == URLQueueEntity.url_id)\
            .all()
        # TODO: This means that there is not a unique key constraint!
        existing_urls = [x[0] for x in existing_urls]
        missing_urls = [x for x in urls if x not in existing_urls]
        assert len(existing_urls) + len(missing_urls) == len(set(urls)), ("Mismatch in the number of URLs to be inputted!", len(existing_urls), len(missing_urls), len(set(urls)), len(urls), existing_urls, missing_urls, urls)
        return existing_urls, missing_urls

    def update_existent_queue_items_visited_again(self, urls):
        """
            Marks the urls
        """
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id) \
            .filter(URLEntity.url.in_(urls))
        query.update({
            URLQueueEntity.occurrences: URLQueueEntity.occurrences + 1
        }, synchronize_session=False)

    def insert_missing_queue_items(self, crawl_next_objects):
        """
            Inserts URLs into the queue
        """
        # Fetch URL ids:
        all_target_urls = [x.target_url for x in crawl_next_objects]
        query = self.session.query(URLEntity.id, URLEntity.url).filter(URLEntity.url.in_(all_target_urls))
        url2id = dict((x[1], x[0]) for x in query)

        # Sort crawl-next-objects by depth
        crawl_next_objects = sorted(crawl_next_objects, key=lambda x: x.depth)

        to_insert = dict()
        for crawl_next_object in crawl_next_objects:
            if crawl_next_object.target_url not in to_insert:
                to_insert[crawl_next_object.target_url] = URLQueueEntity(
                    url_id=url2id[crawl_next_object.target_url],
                    crawler_processing_sentinel=False,
                    crawler_processed_sentinel=False,
                    crawler_skip=crawl_next_object.skip,
                    version_crawl_frontier=self.engine_version,
                    score=crawl_next_object.score,
                    depth=crawl_next_object.depth,
                    occurrences=1
                )
            else:
                to_insert[crawl_next_object.target_url].occurrences += 1

        to_insert = [x for idx, x in to_insert.items()]

        self.session.bulk_save_objects(to_insert)

    def get_duplicate_referral_pairs(self, crawl_next_objects):
        """
            Returns a list of tuples that were already inserted into the referral / adjacency graph
        """
        target_urls = [x.target_url for x in crawl_next_objects]
        referrer_urls = [x.original_url for x in crawl_next_objects]

        id_url_pairs = self.session.query(URLEntity.id, URLEntity.url)\
            .filter(
                sqlalchemy.or_(
                    URLEntity.url.in_(target_urls),
                    URLEntity.url.in_(referrer_urls))
            )\
            .all()
        url2id = dict((x[1], x[0]) for x in id_url_pairs)

        for url in target_urls:
            assert url in url2id, ("You must first insert a target URL before you can add it to the queue!", url)
        for url in referrer_urls:
            assert url in url2id, ("You must first insert a referrer URL before you can add it to the queue!", url)

        all_adjacency_id_pairs = []
        for crawl_next_object in crawl_next_objects:
            # Apply to_from syntax
            all_adjacency_id_pairs.append((
                url2id[crawl_next_object.target_url],
                url2id[crawl_next_object.original_url]
            ))

        # Manifests the (to, from) syntax
        already_inserted_referral_pairs = self.session.query(URLReferralsEntity.target_url_id, URLReferralsEntity.referrer_url_id) \
            .filter(
                sqlalchemy.tuple_(URLReferralsEntity.target_url_id, URLReferralsEntity.referrer_url_id).in_(
                    all_adjacency_id_pairs
                )
            ).all()

        not_inserted_referral_pairs = [x for x in all_adjacency_id_pairs if x not in already_inserted_referral_pairs]
        assert len(already_inserted_referral_pairs) + len(not_inserted_referral_pairs) == len(all_adjacency_id_pairs), ("You should have received less items after checking if an item was inserted already!", len(already_inserted_referral_pairs), len(not_inserted_referral_pairs), len(all_adjacency_id_pairs), already_inserted_referral_pairs, not_inserted_referral_pairs, all_adjacency_id_pairs)

        return already_inserted_referral_pairs, not_inserted_referral_pairs

    def update_visited_referral_entities(self, adjacency_tuples):
        """
            Updates visited adjacency entries by incrementing the occurrences record
            The tuples consist of (to, from) url_id pairs
        """
        visited_referral_entities = self.session.query(URLReferralsEntity.target_url_id, URLReferralsEntity.referrer_url_id) \
            .filter(
            sqlalchemy.tuple_(URLReferralsEntity.target_url_id, URLReferralsEntity.referrer_url_id).in_(
                adjacency_tuples
            )
        )
        visited_referral_entities.update({URLReferralsEntity.occurrences: URLReferralsEntity.occurrences + 1}, synchronize_session=False)

    def insert_referral_entity(self, adjacency_tuples):
        """
            Creates a referral entity / Inserts an item into the web-adjacency graph.
            The tuples consist of (to, from) url_id pairs
        """
        to_insert = []
        for to_url_id, from_url_id in adjacency_tuples:
            url_referral_entity_obj = URLReferralsEntity(
                target_url_id=to_url_id,
                referrer_url_id=from_url_id
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
            if x[0].startswith("tel://"):
                continue
            if x[0].startswith("javascript:"):
                continue
            out.append(CrawlObject(url=x[0], queue_id=x[1], depth=x[2]))

        # Make sure no duplicate entries ...
        assert len([x.url for x in out]) == len(set([x.url for x in out])), ("Non-unique uris found!", len([x.url for x in out]), len(set([x.url for x in out])))

        print("Getting queue (1) takes {:.3f} seconds".format(time.time() - start_time))
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.id.in_([x.queue_id for x in out]))
        query.update({"crawler_processing_sentinel": True}, synchronize_session=False)
        print("Getting queue (2) takes {:.3f} seconds".format(time.time() - start_time))

        return out

    def update_url_task_queue_record_completed(self, urls):
        """
            implements part of the pop operation for queue,
            indicating that a crawler has processed the request successfully
        """
        query = self.session.query(URLQueueEntity).filter(URLQueueEntity.url_id == URLEntity.id).filter(
            URLEntity.url.in_(urls))
        # print("Number of items before processed: ", query.filter(URLQueueEntity.crawler_processed_sentinel == false()).count())
        query.update({"crawler_processed_sentinel": True}, synchronize_session=False)
        # print("Number of items now processed: ", query.filter(URLQueueEntity.crawler_processed_sentinel == false()).count())

    def update_url_task_queue_record_failed(self, urls):
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

    def insert_markup_record(self, crawl_objects):
        """
        :param url_markup_tuple_dict: Dictionary of url -> markup
        """
        print("URL Markup tuple dict is: ", len(crawl_objects))
        urls = [x.url for x in crawl_objects]

        inserted_markup_urls = self.session.query(URLEntity.url) \
            .filter(URLEntity.url.in_(urls)) \
            .join(RawMarkup) \
            .all()
        inserted_markup_urls = [x[0] for x in inserted_markup_urls]

        query = self.session.query(URLEntity.id, URLEntity.url).filter(URLEntity.url.in_(urls)).all()
        url2id = dict((x[1], x[0]) for x in query)

        # Only keep items that are not inserted yet
        to_insert = []
        c = 0
        for crawl_object in crawl_objects:
            if crawl_object.url in inserted_markup_urls:
                c += 1
                continue
            assert crawl_object.markup, crawl_object.markup
            obj = RawMarkup(
                url_id=url2id[crawl_object.url],
                markup=crawl_object.markup,
                spider_processing_sentinel=False,
                spider_processed_sentinel=False,
                spider_skip=False,
                version_spider=self.engine_version
            )
            to_insert.append(obj)

        assert len(inserted_markup_urls) + len(to_insert) == len(crawl_objects), ("Lengths are weird!", len(inserted_markup_urls), len(to_insert), len(crawl_objects))

        print("Bulk inserting raw_markup {} skipping {}".format(len(to_insert), c))
        # Bulk save all the markups that were fetched

        self.session.bulk_save_objects(to_insert)

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
