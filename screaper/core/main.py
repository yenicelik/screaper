"""
    Includes the main application loop
"""
import asyncio
import random
import string
import time
import numpy as np

from screaper_resources.resources.db import Database
from screaper.crawl_frontier.crawl_frontier import CrawlFrontier, CrawlObjectsBuffer
from screaper.downloader.async_crawl_task import CrawlAsyncTask
from screaper_resources.resources.resouces_proxylist import ProxyList

class Main:

    def __init__(self, name="", database=None):
        self.name = name
        # Start the needed resources
        self.proxy_list = ProxyList()

        assert database
        self.resource_database = database
        self.crawl_objects_buffer = CrawlObjectsBuffer()
        self.crawl_frontier = CrawlFrontier(database=self.resource_database, crawl_objects_buffer=self.crawl_objects_buffer)

        # Implement an async-queue

        self.ping_interval = 5  # How many seconds to run the ping interval for
        self.timestamps = []
        self.task_durations = [30., ] # Adding as an initial starting point s.t. we don't have division by zero or nan ops

    def calculate_sites_per_minute(self, crawled_sites):
        """
            Calculates how many sites we can crawl per hour
        """
        self.timestamps.insert(0, (time.time(), crawled_sites))

        if len(self.timestamps) > (86500 // 5):
            self.timestamps = self.timestamps[:(86500 // 5)]

        sites_per_second = (self.timestamps[0][1] - self.timestamps[-1][1])
        sites_per_second /= (self.timestamps[0][0] - self.timestamps[-1][0]) + 1

        sites_per_minute = sites_per_second * 60

        return sites_per_minute

    async def task(self, async_crawl_task):
        """
            Consumes the CrawlAsyncTasks produced into the queue above
        """
        start_time = time.time()
        crawl_object = await async_crawl_task.fetch()
        self.crawl_objects_buffer.add_to_buffer(crawl_object)
        self.task_durations.append(time.time() - start_time)

    async def dispatch_crawl_objects(self, crawl_object):
        return asyncio.create_task(self.task(CrawlAsyncTask(self.proxy_list, crawl_object=crawl_object)))

    async def run_main_loop(self):

        self.crawl_objects_buffer.flush_buffer()

        while True:

            start_time = time.time()

            crawled_sites = self.resource_database.get_number_of_crawled_sites()
            queued_sites = self.resource_database.get_number_of_queued_urls()
            sites_per_minute = self.calculate_sites_per_minute(crawled_sites)
            average_time_per_task = np.median(self.task_durations)
            proxy_success_rate = self.proxy_list.proxy_list_success_rate
            print("Process {} :: Global Sites per s/m/h: {:.2f}/{:.1f}/{:.1f} -- Crawled sites: {} -- Available proxies: {}".format(self.name, sites_per_minute / 60, sites_per_minute, sites_per_minute * 60, crawled_sites, len(self.proxy_list._proxies.difference(self.proxy_list._proxies_blacklist))))
            print("Process {} :: AVG Time per Task: {:.2f} -- Proxy success rate: {:.1f} -- Queue sites in DB: {}".format(self.name, average_time_per_task, proxy_success_rate, queued_sites))

            # Fetch next items to be worked on
            crawl_objects = self.crawl_frontier.get_next_urls_to_crawl()
            self.resource_database.commit()

            # Run the tasks
            tasks = []
            for crawl_object in crawl_objects:
                # Spawn a AsyncCrawlTask object
                task = self.dispatch_crawl_objects(crawl_object)
                tasks.append(task)

            # Such that it doesn't spam
            await asyncio.sleep(2)

            # Wait until all tasks are handled
            if tasks:
                await asyncio.gather(*tasks)
                print("Time until gather took: ", time.time() - start_time)

            print("Flushing records: Markups {} -- Failed {} -- Completed {} -- Total {}".format(self.crawl_objects_buffer.calculate_collected_markups(), self.crawl_objects_buffer.calculate_failed(), self.crawl_objects_buffer.calculate_successful(), self.crawl_objects_buffer.calculate_total()))
            flush_start_time = time.time()

            # Flush all items into the database
            self.crawl_frontier.insert_markups_for_successul_crawl_objects()
            self.crawl_frontier.extend_frontier()
            self.crawl_frontier.mark_crawl_objects_as_done()
            print("Flushing took {:.3f} second".format(time.time() - flush_start_time))

            # Re-iniate all buffers
            self.crawl_objects_buffer.flush_buffer()
            self.resource_database.commit()


if __name__ == "__main__":
    print("Starting the application")
    resource_database = Database()  # TODO Make database async!

    name = 'PROC:' + ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
    print("argv is: ", name)
    main = Main(name=name, database=resource_database)

    asyncio.run(main.run_main_loop())
