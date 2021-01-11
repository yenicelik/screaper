"""
    Implements a crawl frontier
"""
import time

from dotenv import load_dotenv

load_dotenv()


class CrawlFrontier:
    """
        Poses as a middleware between the Database, and the Buffer accumulated
    """

    def __init__(self, database, crawl_objects_buffer):
        self.crawl_objects_buffer: CrawlObjectsBuffer = crawl_objects_buffer
        self.database = database

    def get_next_urls_to_crawl(self):
        """
            Pops a list of 512 items which will be scraped next
        """
        start_time = time.time()
        crawl_objects = self.database.get_url_task_queue_record_start_list()
        print("Time to populate queue took: ", time.time() - start_time)
        return crawl_objects

    def extend_frontier(self):
        """
            Insert non-existent URL entities
            Insert non-existent URLQueue entities
            Insert non-existent URLReferral entities

            This makes extensive use of the CrawlNextObjects Class
        """
        crawl_next_objects = self.crawl_objects_buffer.generate_crawl_next_objects()
        newly_found_urls = [x.target_url for x in crawl_next_objects]

        # Insert into the database if not existent yet
        to_be_inserted_urls = self.database.get_url_entity_not_inserted(newly_found_urls)
        self.database.insert_url_entity(to_be_inserted_urls)

        # Update all items in the queue by incrementing the retry and occurrence counter
        existing_urls, _ = self.database.get_url_queue_inserted_and_missing(newly_found_urls)
        self.database.update_existent_queue_items_visited_again(existing_urls)
        # Insert into the queue if not yet existent
        missing_crawl_next_objects = [x for x in crawl_next_objects if x.target_url not in existing_urls]
        self.database.insert_missing_queue_items(missing_crawl_next_objects)

        # Insert as a referral pair, if not yet existent
        already_inserted_referral_pairs, not_inserted_referral_pairs = self.database.get_duplicate_referral_pairs(
            crawl_next_objects)
        self.database.update_visited_referral_entities(
            already_inserted_referral_pairs)  # Need to apply the database migration first
        self.database.insert_referral_entity(not_inserted_referral_pairs)

    def insert_markups_for_successul_crawl_objects(self):
        """
            Insert the markup if the crawl_object successfully scraped a page
        """
        crawl_objects = self.crawl_objects_buffer.get_successful_items()
        self.database.insert_markup_record(crawl_objects)

    def mark_crawl_objects_as_done(self):
        """
            Depending on the crawl object, marks them as completed (if markup was successfully received), or failed (if no markup was fetched, or a bad status is returned)
        """
        # Mark the failed items as failed in the database
        self.database.update_url_task_queue_record_completed(self.crawl_objects_buffer.get_successful_items())
        self.database.update_url_task_queue_record_failed(self.crawl_objects_buffer.get_failed_items())

    def rollback(self):
        self.database.update_url_task_queue_record_failed(self.crawl_objects_buffer.buffer)


class CrawlObjectsBuffer:

    def __init__(self):
        self.buffer = set()

        # Variables to be calculated over time
        self._successful_items = None
        self._failed_items = None

    def flush_buffer(self):
        self.buffer = set()

    def add_to_buffer(self, crawl_object):
        assert isinstance(crawl_object, CrawlObject)
        self.buffer.add(crawl_object)

    def calculate_successful(self):
        return len({x for x in self.buffer if not x.not_successful})

    def calculate_failed(self):
        return len({x for x in self.buffer if x.not_successful})

    def calculate_collected_markups(self):
        return len({x for x in self.buffer if x.markup})

    def calculate_total(self):
        return len(self.buffer)

    def get_successful_items(self):
        self._successful_items = [x for x in self.buffer if not x.not_successful]
        return self._successful_items

    def get_failed_items(self):
        self._failed_items = [x for x in self.buffer if x.not_successful]
        return self._failed_items

    def get_all_items(self):
        return self.buffer

    def generate_crawl_next_objects(self):
        out = [x for crawl_object in self.buffer for x in crawl_object.crawl_next_objects]
        return out

class CrawlObject:

    def __init__(self, url, queue_id, depth):
        # Do a bunch of more asserts on the type
        assert url or url == "", url
        assert queue_id or queue_id == 0, queue_id
        assert depth or depth == 0, depth

        # Could probably even make this more string by applying a regex on the url
        assert isinstance(url, str), (url, type(url))
        assert isinstance(queue_id, int), (queue_id, type(queue_id))
        assert isinstance(depth, int), (depth, type(depth))

        self.url = url
        self.queue_id = queue_id
        self.depth = depth

        # Items that will be assigned during the runtime
        self.status_code = None
        self.crawl_next_objects: [CrawlNextObject] = []  # A list of CrawlNextObjects
        self.markup = None
        self.score = None
        self.url_id = None
        self.ok = None

        self.not_successful = False
        self.errors = []

    def insert_crawl_next_object(self, original_crawl_obj, target_url, skip, score):
        obj = CrawlNextObject(
            original_url=original_crawl_obj.url,
            target_url=target_url,
            skip=skip,
            depth=original_crawl_obj.depth + 1,
            score=score
        )
        self.crawl_next_objects.append(obj)

    def add_error(self, err):
        self.errors.append(err)
        self.not_successful = True

        self.score = 0


class CrawlNextObject:

    def __init__(self, original_url, target_url, skip, depth, score):
        self.original_url = original_url
        self.target_url = target_url
        self.skip = skip
        self.depth = depth
        self.score = score


if __name__ == "__main__":
    print("Check the crawl frontier")
