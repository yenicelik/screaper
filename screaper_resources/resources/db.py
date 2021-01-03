import asyncio
import os
import sqlalchemy

from dotenv import load_dotenv
from sqlalchemy import false, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import screaper
from screaper_resources.resources.entities import URLQueueEntity, URLEntity, URLReferralsEntity, RawMarkup, \
    NamedEntities

load_dotenv()


class Queries:
    """
        Class to pre-build and log all the queries
    """

    @staticmethod
    def get_url_exists(session, url):
        url_entity = session.query(URLEntity) \
            .filter(URLEntity.url == url) \
            .one_or_none()

        return url_entity

    @staticmethod
    def get_raw_markup_count(session):
        return session.query(RawMarkup).count()

    @staticmethod
    def get_number_of_queued_urls(session):
        return session.query(URLQueueEntity).count()

    @staticmethod
    def get_markup_exists(session, url):
        url_entity = session.query(URLEntity) \
            .filter(URLEntity.url == url) \
            .join(RawMarkup) \
            .one_or_none()

        return url_entity

    @staticmethod
    def add_markup_to_index(session, url, markup):
        # For now, analyse any kind of markup
        Queries.create_markup_record(session=session, url=url, markup=markup)

    @staticmethod
    def create_markup_record(session, url, markup, engine_version="0.0.1"):
        url_entity = session.query(URLEntity) \
            .filter(URLEntity.url == url) \
            .one_or_none()

        # generate a random 64-bit random string
        obj = RawMarkup(
            url_id=url_entity.id,
            markup=markup,
            spider_processing_sentinel=False,
            spider_processed_sentinel=False,
            spider_skip=False,
            version_spider=engine_version
        )
        session.add(obj)

    @staticmethod
    def create_url_entity(session, url, engine_version="0.0.1"):
        url_entity_obj = session.query(URLEntity) \
            .filter(URLEntity.url == url) \
            .one_or_none()

        # Add the URL Into the global Queue
        if url_entity_obj is None:
            # Create a URL Object
            url_entity_obj = URLEntity(
                url=url,
                engine_version=engine_version
            )
            session.add(url_entity_obj)

        return url_entity_obj

    @staticmethod
    def create_url_queue_entity(session, url_entity_obj, skip, engine_version="0.0.1"):
        url_queue_obj = session.query(URLQueueEntity) \
            .filter(URLQueueEntity.url_id == url_entity_obj.id) \
            .one_or_none()

        # Add to the queue if not already within the queue
        if url_queue_obj is None:
            url_queue_obj = URLQueueEntity(
                url_id=url_entity_obj.id,
                crawler_processing_sentinel=False,
                crawler_processed_sentinel=False,
                crawler_skip=skip,
                version_crawl_frontier=engine_version
            )
            session.add(url_queue_obj)
        else:
            url_queue_obj.occurrences += 1

        return url_queue_obj

    @staticmethod
    def create_referral_entity(session, url_entity, referrer_url):

        referrer_url_entity_obj = session.query(URLEntity) \
            .filter(URLEntity.url == referrer_url) \
            .one_or_none()

        # Only for the target_url, check if this is already in the queue
        # The referrer_url should be scraped by definition
        url_referral_entity_obj = session.query(URLReferralsEntity) \
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
            session.add(url_referral_entity_obj)

        return url_referral_entity_obj

    @staticmethod
    def get_url_task_queue_record_completed(session, url):
        obj = session.query(URLEntity) \
            .filter(URLEntity.url == url) \
            .join(URLQueueEntity) \
            .first()

        # TODO: Will this update the sub-object in the database? (because join?)
        obj.crawler_processed_sentinel = True
        assert obj.crawler_processed_sentinel, obj.crawler_processed_sentinel
        return obj

    @staticmethod
    def get_url_task_queue_record_failed(session, url, max_retries=5):
        obj = session.query(URLQueueEntity) \
            .join(URLEntity) \
            .filter(URLEntity.url == url) \
            .one()

        # TODO: Will this update the sub-object in the database? (because join?)
        # If retried too many times and failed, skip
        skip = obj.retries + 1 >= max_retries
        obj.crawler_processing_sentinel = False
        obj.crawler_processed_sentinel = False
        obj.skip = skip
        obj.retries += 1
        return obj

    @staticmethod
    def get_url_task_queue_record_start_list(session, max_retries=5):
        """
            Retrieve a list of URL sites to retrieve
        :return:
        """
        # Doesnt make much sense to retrieve and set a sentinel for this, I think
        query_list = session.query(URLEntity, URLQueueEntity) \
            .filter(URLQueueEntity.crawler_processing_sentinel == false()) \
            .filter(URLQueueEntity.retries < max_retries) \
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


class Database:
    """
        Wrapper to handle all I/O with the database.

        Implements basic CRUD operations

        Actually, let's not implement CRUD, but the actual operations that are used.
        The CRUD is already implemented by the ORM
    """

    def __init__(self):
        self.queries = Queries()

        db_asyn_url = os.getenv('AsyncDatabaseUrl')
        db_url = os.getenv('DatabaseUrl')

        self.sync_engine = create_engine(db_url, encoding='utf8')
        Session = sessionmaker()
        Session.configure(bind=self.sync_engine)
        self.sync_session = Session()

        self.async_engine = create_async_engine(db_asyn_url, encoding='utf8', echo=False)
        print("Engine is: ", self.async_engine)
        self.async_session = AsyncSession(bind=self.async_engine)
        self.async_session.begin()

        print("Created session: ", self.async_session)

        self.max_retries = 4
        self.engine_version = "0.0.1"

    # TODO: Somehow there is a bug when both commit messages are active
    def sync_commit(self):
        self.sync_session.commit()

    def commit(self):
        self.async_session.commit()

    async def create_url_entity(self, url):
        out = await self.async_session.run_sync(self.queries.create_url_entity, url)
        return out

    async def create_url_queue_entity(self, url_entity_obj, skip):
        out = await self.async_session.run_sync(self.queries.create_url_queue_entity, url_entity_obj, skip)
        await self.async_session.commit()
        return out

    async def create_referral_entity(self, url_entity, referrer_url):
        out = await self.async_session.run_sync(self.queries.create_referral_entity, url_entity, referrer_url)
        await self.async_session.commit()
        return out

    async def get_url_task_queue_record_completed(self, url):
        """
            implements part of the pop operation for queue,
            indicating that a crawler has processed the request successfully
        """
        out = await self.async_session.run_sync(self.queries.get_url_task_queue_record_completed, url)
        await self.async_session.commit()
        return out

    async def get_url_task_queue_record_failed(self, url):
        """
            implements the pop operation for queue
            indicating that a crawler has processed the request successfully
        """
        out = await self.async_session.run_sync(self.queries.get_url_task_queue_record_failed, url)
        await self.async_session.commit()
        return out

    async def get_url_exists(self, url):
        out = await self.async_session.run_sync(self.queries.get_url_exists, url)
        await self.async_session.commit()
        return out

    async def get_markup_exists(self, url):
        url_entity = await self.async_session.run_sync(self.queries.get_markup_exists, url)
        print("url_entity is: ", url_entity)
        return url_entity

    async def get_number_of_queued_urls(self):
        result = await self.async_session.run_sync(self.queries.get_number_of_queued_urls)
        print("result is: ", result)
        return result

    async def get_number_of_crawled_sites(self):
        result = await self.async_session.run_sync(self.queries.get_raw_markup_count)
        print("result is: ", result)
        return result

    async def get_url_task_queue_record_start_list(self):
        """
            Retrieve a list of URL sites to retrieve
        :return:
        """
        out = await self.async_session.run_sync(self.queries.get_url_task_queue_record_start_list)
        await self.async_session.commit()
        return out

    #######
    # Heavy load calls. These are handled over async
    #######
    async def add_markup_to_index(self, url, markup):
        await self.async_session.run_sync(self.queries.add_markup_to_index, url, markup)
        await self.async_session.commit()

    async def create_markup_record(self, url, markup):
        await self.async_session.run_sync(self.queries.create_markup_record, url, markup)
        await self.async_session.commit()

    # # TODO: Gotta re-implement these
    # def get_all_indexed_markups(self, dev=False):
    #     with self.engine.connect() as connection:
    #         query_result = connection.execute("SELECT url, markup, raw_markup.id AS markup_id FROM url, raw_markup WHERE url.id = raw_markup.url_id {};".format("ORDER BY RANDOM() LIMIT 16" if dev else ""))
    #         column_names = query_result.keys()
    #         query_result = query_result.fetchall()
    #
    #     print("Query result:", query_result)
    #     print("Column names: ", column_names)
    #
    #     df = pd.DataFrame(query_result, columns=column_names)
    #     return df
    #
    # def add_named_entity_candidate(self, objs):
    #     for obj in objs:
    #         print("Inserting: ", obj)
    #         named_entity_obj = NamedEntities(**obj)
    #         self.session.add(named_entity_obj)


if __name__ == "__main__":
    print("Handle all I/O")

    print("Checking some very basic operations with async I/O")

    db = Database()


    # Possibly move this to a test file

    async def run_all():
        # await db.get_number_of_crawled_sites()
        # await db.get_number_of_queued_urls()
        url = "https://www.thomasnet.com/catalogs/mechanical-components-and-assemblies/bearings/"
        await db.get_markup_exists(url)


    asyncio.run(run_all())

    print("Done!")
