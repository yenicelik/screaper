"""
    Any tests related to the database
"""
from flashtext import KeywordProcessor

from screaper.core.seed_setter import SeedSetter
from screaper.crawl_frontier.crawl_frontier import CrawlFrontier, CrawlObjectsBuffer
from screaper.downloader.async_crawl_task import CrawlAsyncTask
from screaper.engine.markup_processor import markup_processor, LinkProcessor
from screaper_resources.resources.db import Database
from screaper_resources.resources.entities import Base, ActorEntityCandidates, NamedEntities, ProcessedMarkup, \
    RawMarkup, URLReferralsEntity, URLQueueEntity, URLEntity

# TODO: Check duplicate inputs
from screaper_resources.resources.resouces_proxylist import ProxyList


class PostgresTests:

    def setUp(self):
        db_url = "postgresql://postgres@localhost:5432/test_database"

        # Generate database if not existent yet
        self.database = Database(db_url)

        # drop all tables
        for tbl in [ActorEntityCandidates, NamedEntities, ProcessedMarkup, RawMarkup, URLReferralsEntity,
                    URLQueueEntity, URLEntity]:
            # Check if table exists
            try:
                self.database.engine.execute(tbl.__table__.delete())
            except Exception as e:
                print(repr(e))

        # create all tables
        Base.metadata.create_all(self.database.engine)

        ## Finally anything non-db related

        self.keyword_processor = KeywordProcessor()
        self.keyword_processor.add_keywords_from_list(['bearing'])

        self.link_processor = LinkProcessor()

        self.crawl_objects_buffer = CrawlObjectsBuffer()
        self.crawl_frontier = CrawlFrontier(database=self.database, crawl_objects_buffer=self.crawl_objects_buffer)

    def _test_seed_insert(self):

        self.seed_urls = [
            "",
            "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html",  # category depth 2
            "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide",
            "https://www.dtr-ihk.de/mitgliedschaft/mitgliederverzeichnis",
            "https://www.wlw.ch/",
            "https://www.europages.de/Maschinenbau%20und%20Industrie%20-%20Ausr%C3%BCstungen.html"
        ]

        # Insert seed URLs
        seed_setter = SeedSetter(self.database)

        # Check if inserted URLs items correspond exactly
        inserted_urls = self.database.session.query(URLEntity.url).all()
        inserted_urls = [x[0] for x in inserted_urls]
        assert len(inserted_urls) == len(self.seed_urls), (inserted_urls, self.seed_urls)
        for seed_url in self.seed_urls:
            assert seed_url in inserted_urls, (seed_url, inserted_urls)
        for inserted_url in inserted_urls:
            assert inserted_url in self.seed_urls, (inserted_url, self.seed_urls)

        # Check if queue items correspond exactly
        inserted_queue_items = self.database.session.query(URLEntity, URLQueueEntity) \
            .filter(URLEntity.id == URLQueueEntity.url_id) \
            .all()

        # Account for the empty item inserted
        assert len(inserted_queue_items) + 1 == len(self.seed_urls), (
        [x[0].url for x in inserted_queue_items], self.seed_urls)

        # Check if every item in the queue contains exactly one seed item
        for url_entity, url_queue_entity in inserted_queue_items:
            assert url_entity.url in self.seed_urls, url_entity.url
            assert not url_queue_entity.crawler_skip, url_queue_entity.crawler_skip
            assert not url_queue_entity.crawler_processing_sentinel, url_queue_entity.crawler_processing_sentinel
            assert not url_queue_entity.crawler_processed_sentinel, url_queue_entity.crawler_processed_sentinel

        # Check if every seed URL was successfully inserted into the queue
        for seed_url in self.seed_urls:
            if seed_url == "":
                continue
            queued_urls = [x[0].url for x in inserted_queue_items]
            assert seed_url in queued_urls, (seed_url, queued_urls)

    def _mock_markup(self):
        return """
            <!DOCTYPE html>
            <html>
            <body>
            <h1>My First Heading</h1>
            <a href="www.google.com">My First Heading</a>
            <a href="www.facebook.com">My first paragraph.</a>
            </body>
            </html>
        """

    def _test_url_get_and_update(self):
        # Pick one of the URL items
        crawl_objects = self.crawl_frontier.get_next_urls_to_crawl(n=2)
        self.database.commit()

        # Check that the items for the crawl objects were set to processing
        for crawl_object in crawl_objects:
            queue_entity = self.database.session.query(URLQueueEntity) \
                .filter(URLQueueEntity.url_id == crawl_object.url_id) \
                .one_or_none()
            assert queue_entity
            assert queue_entity.crawler_processing_sentinel, (
            queue_entity.id, queue_entity.url_id, queue_entity.crawler_processing_sentinel)
            assert not queue_entity.crawler_processed_sentinel, (
            queue_entity.id, queue_entity.url_id, queue_entity.crawler_processing_sentinel)

        return crawl_objects

    def _test_url_is_inserted_into_markup(self, crawl_objects):
        previous_url_ids = [x.url_id for x in crawl_objects]
        query = self.database.session.query(URLEntity, RawMarkup).filter(URLEntity.id == RawMarkup.url_id).all()
        url_entities, raw_markups = [x[0] for x in query], [x[1] for x in query]
        assert len(raw_markups) == 2, (len(raw_markups),)
        for url_entity, raw_markup in zip(url_entities, raw_markups):
            print(url_entity, type(url_entity), raw_markup, type(raw_markup))
            assert url_entity.id == raw_markup.url_id, (
            url_entity.id, type(url_entity), raw_markup.url_id, type(raw_markup))
        for url_entity in url_entities:
            assert url_entity.id in previous_url_ids, (url_entity.id, previous_url_ids)
        for url in previous_url_ids:
            assert url in [url_entity.id for url_entity in url_entities], (
                url, [url_entity.id for url_entity in url_entities])

    def _test_frontier_was_successfully_expanded(self, urls, existing_urls):
        # Check that each url_id within the queue indeed references url.id
        # Check if inserted URLs and Queue items correspond exactly

        # Check that each url_id within the referral graph indeed references url.id
        # to_be_inserted_urls = self.database.get_url_entity_not_inserted(newly_found_urls)
        # self.database.insert_url_entity(to_be_inserted_urls)

        query = self.database.session.query(URLEntity, URLQueueEntity) \
            .filter(URLEntity.id == URLQueueEntity.url_id) \
            .filter(URLEntity.url.in_(urls)) \
            .all()

        # Assert 6 items in total in queue now:
        assert len(query) == 7, (len(query), [x[0].url for x in query])

        for x in query:
            url_entity, url_queue_entity = x[0], x[1]

            if url_entity.url in existing_urls:
                assert url_entity.url not in ["www.google.com/", "www.facebook.com/"], (url_entity.url,)
                assert url_queue_entity.crawler_skip == False, (url_queue_entity.crawler_skip,)
                assert url_queue_entity.crawler_processed_sentinel == False, (url_queue_entity.crawler_processed_sentinel, url_entity.url)
                assert url_queue_entity.depth == 0, ("Depth is not null!", url_queue_entity.depth)
            else:
                assert url_entity.id == url_queue_entity.url_id, (url_entity.id, url_queue_entity.url_id)
                assert url_entity.url in ["www.google.com/", "www.facebook.com/"], (url_entity.url,)
                assert url_queue_entity.crawler_skip == True, (url_queue_entity.crawler_skip,)
                assert url_queue_entity.crawler_processing_sentinel == False, (url_queue_entity.crawler_processing_sentinel, url_entity.url)
                assert url_queue_entity.crawler_processed_sentinel == False, (url_queue_entity.crawler_processed_sentinel, url_entity.url)
                assert url_queue_entity.depth == 1, ("Depth is not one!", url_queue_entity.depth)

        assert len([x for x in query if x[0].url in existing_urls]) == 5, [x for x in query if x[1] in existing_urls]
        assert len([x for x in query if x[0].url not in existing_urls]) == 2, [x for x in query if x[1] not in existing_urls]

        assert url_queue_entity.crawler_processing_sentinel in (True, False), (url_queue_entity.crawler_processing_sentinel, url_entity.url)

        # Update all items in the queue by incrementing the retry and occurrence counter
        # existing_urls, _ = self.database.get_url_queue_inserted_and_missing(newly_found_urls)
        # self.database.update_existent_queue_items_visited_again(existing_urls)
        # for existing_url in existing_urls:
        #     self.database.session.query(URLEntity).filter(URLEntity.url == existing_url)

        # Make sure that the queue consists of the old items, plus the new ones
        all_inserted_urls = self.database.session.query(URLEntity).all()
        all_inserted_urls = [x.url for x in all_inserted_urls]
        assert len(set(all_inserted_urls)) == 5 + 2 + 1, ("Not right number of items in queue", len(all_inserted_urls), all_inserted_urls)

        all_inserted_urls = self.database.session.query(URLQueueEntity).all()
        # all_inserted_urls = [x[0] for x in all_inserted_urls]
        assert len(set(all_inserted_urls)) == 5 + 2, ("Not right number of items in queue", all_inserted_urls)

        all_inserted_urls = self.database.session.query(URLEntity, URLQueueEntity).filter(
            URLEntity.id == URLQueueEntity.url_id).all()
        assert len(set(all_inserted_urls)) == 5 + 2, ("Not right number of items in queue", all_inserted_urls)
        for url_entity, url_queue_entity in all_inserted_urls:
            assert url_entity.id == url_queue_entity.url_id, (url_entity.id, url_queue_entity.url_id)

        query = self.database.session.query(URLEntity).all()
        id2url = dict([(url_entity.id, url_entity.url) for url_entity in query])

        supposed_all_inserted_pairs = [
            ("www.google.com/", "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html"),
            ("www.facebook.com/", "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html"),
            ("www.google.com/", "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide"),
            ("www.facebook.com/", "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide")
        ]

        referrals_query = self.database.session.query(URLEntity, URLReferralsEntity) \
            .filter(URLEntity.id == URLReferralsEntity.referrer_url_id) \
            .all()

        # Number of referral items should be 4 in total
        assert len([x for x in referrals_query if x[0].url != ""]) == 4, (len(query), [x[0].url for x in referrals_query])

        # Make sure all url entities are corresponding
        for url_entity, url_referral_entity in referrals_query:
            assert url_entity.id == url_referral_entity.referrer_url_id, (url_entity.id, url_referral_entity.referrer_url_id)

            target_url = id2url[url_referral_entity.target_url_id]
            referrer_url = id2url[url_referral_entity.referrer_url_id]

            if target_url in ("www.google.com/", "www.facebook.com/"):
                assert (target_url, referrer_url) in supposed_all_inserted_pairs, (target_url, referrer_url)
                assert url_referral_entity.occurrences == 1, (url_referral_entity.occurrences, 1)

    def _test_crawl_objects_are_successfully_marked(self, newly_inserted_urls):
        query = self.database.session.query(URLEntity, URLQueueEntity) \
            .filter(URLEntity.id == URLQueueEntity.url_id) \
            .all()

        print("Inserted urls: ", newly_inserted_urls)
        for url_entity, url_queue in query:
            assert url_queue.occurrences in (1, 2), (url_queue.occurrences,)

            assert url_entity.id == url_queue.url_id, (url_entity.id, url_queue.url_id)

            if url_entity.url in newly_inserted_urls:
                assert url_queue.crawler_processing_sentinel == False, (url_queue.crawler_processing_sentinel,)
                assert url_queue.crawler_processed_sentinel == False, (url_queue.crawler_processed_sentinel,)
                assert url_queue.crawler_skip == True, (url_queue.skip,)
                assert url_queue.depth == 1, (url_queue.depth,)

                # Make sure the newly items correspond to facebook or google.com
                assert url_entity.url in ("www.facebook.com/", "www.google.com/"), (url_entity.url,)
            else:
                assert url_queue.crawler_skip == False, (url_queue.skip,)
                assert url_queue.depth == 0, (url_queue.depth,)

                assert url_entity.url not in ("www.facebook.com/", "www.google.com/"), (url_entity.url,)

        assert len([x[0].url for x in query if x[1].crawler_processing_sentinel]) == 2, [x[0].url for x in query if x[1].crawler_processing_sentinel]
        assert len([x[0].url for x in query if x[1].crawler_processed_sentinel]) == 2, [x[0].url for x in query if x[1].crawler_processed_sentinel]

    def run_successfully_inserted_tests(self):
        """
            Assume everything is successful
        """

        self.setUp()

        self._test_seed_insert()

        crawl_objects = self._test_url_get_and_update()

        for crawl_object in crawl_objects:

            ########################################
            # MOCK THE HTML REQUEST
            ########################################

            # Insert new item into the URL
            # Act as if a markup is parsed with two links
            proxy_list = ProxyList()
            crawl_async_task = CrawlAsyncTask(proxy_list=proxy_list, crawl_object=crawl_object)
            crawl_async_task.crawl_object.markup = self._mock_markup()
            crawl_async_task.crawl_object.status_code = 200

            crawl_async_task.crawl_object.score = crawl_async_task.score(crawl_async_task.crawl_object.markup)

            found_urls = markup_processor.get_links(crawl_async_task.url, crawl_async_task.crawl_object.markup)
            # Process all the links # Propagate the score onwards
            for found_url in found_urls:
                target_url, referrer_url, _ = self.link_processor.process(target_url=found_url,
                                                                          referrer_url=crawl_async_task.crawl_object.url)
                # For the sake of test, do not skip these items
                skip = True
                print("Inserting target and referral items: ", target_url, referrer_url, skip)
                crawl_object.insert_crawl_next_object(original_crawl_obj=crawl_async_task.crawl_object,
                                                      target_url=target_url, skip=skip,
                                                      score=crawl_async_task.crawl_object.score)

            assert crawl_object.markup
            saved_target_urls = [x.target_url for x in crawl_object.crawl_next_objects]
            print("Target urls are: ", saved_target_urls)
            assert set(saved_target_urls) == set(["www.google.com/", "www.facebook.com/"]), set(saved_target_urls)
            assert len(saved_target_urls) == 2, saved_target_urls

            self.crawl_objects_buffer.add_to_buffer(crawl_object)

        assert len(self.crawl_objects_buffer.buffer) == 2, (len(self.crawl_objects_buffer.buffer), 2)

        # Insert all items into the database
        # Flush all items into the database

        print("Items in buffer are: ", self.crawl_objects_buffer.buffer)
        for x in self.crawl_objects_buffer.buffer:
            print(x)

        # Make sure that each uri was inserted exactly once, and that there is a new markup for each such item
        # Insert new markup into the Markup items
        self.crawl_frontier.insert_markups_for_successful_crawl_objects()
        self._test_url_is_inserted_into_markup(crawl_objects)

        # Make sure that each new target uri was correctly inserted into all tables
        self.crawl_frontier.extend_frontier()
        self._test_frontier_was_successfully_expanded(
            urls=self.seed_urls + ["www.google.com/", "www.facebook.com/"],
            existing_urls=self.seed_urls
        )

        self.crawl_frontier.mark_crawl_objects_as_done()
        self._test_crawl_objects_are_successfully_marked(newly_inserted_urls=["www.google.com/", "www.facebook.com/"])

        self.crawl_objects_buffer.flush_buffer()
        assert not self.crawl_objects_buffer.buffer, self.crawl_objects_buffer.buffer


if __name__ == "__main__":
    print("Database tests")
    tests = PostgresTests()
    tests.run_successfully_inserted_tests()
