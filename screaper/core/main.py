"""
    Includes the main application loop
"""
import asyncio
import time
import numpy as np

import requests

from screaper.crawl_frontier.crawl_frontier import CrawlFrontier

from screaper.downloader.async_crawl_task import CrawlAsyncTask
from screaper_resources.resources.db import Database
from screaper_resources.resources.resouces_proxylist import ProxyList


class Main:

    # TODO: Add depth to URLs, s.t. we can apply breadth first search

    def __init__(self, name=""):
        self.name = name
        # Start the needed resources
        self.proxy_list = ProxyList()
        self.resource_database = Database()  # TODO Make database async!

        self.crawl_frontier = CrawlFrontier(resource_database=self.resource_database)

        # Implement an async-queue

        self.ping_interval = 5  # How many seconds to run the ping interval for

        self.active_workers_count = 0

        self.timestamps = []

        self.task_durations = [30., ] # Adding as an initial starting point s.t. we don't have division by zero or nan ops

        self.flush_buffers()

    def flush_buffers(self):
        # Lists to be flushed every now and then for database bulk operations
        self.buffer_markup_records = dict()  # This buffer is a dictionary for more efficient lookup and insert
        self.buffer_queue_entry_completed = []
        self.buffer_queue_entry_failed = []

    def calculate_sites_per_minute(self, crawled_sites):
        """
            Calculates how many sites we can crawl per hour
        :param crawled_sites:
        :return:
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
        :return:
        """

        # Just spawn new threads while the queue is not empty

        start_time = time.time()

        # Get from queue
        # Consume half the queue
        status_code, markup, target_urls = await async_crawl_task.fetch()

        # TODO: Put these into a queue with different topics.
        # Depending on the topic, flush them into differen pop_failed, pop_verify or add_to_index

        # If an error is returned, just skip it:
        if status_code is None:
            # print("Some error happened!")
            self.buffer_queue_entry_failed.append(async_crawl_task.url)
            return
        else:
            # print("Made request to web server and got response", status_code, len(markup), len(target_urls))
            pass

        # Push them into the database
        if not (status_code == requests.codes.ok):
            # print("Not an ok status code!")
            self.buffer_queue_entry_failed.append(async_crawl_task.url)
        else:
            # print("Adding to database")
            self.buffer_markup_records[async_crawl_task.url] = markup

        for target_url in target_urls:
            # TODO: Add the success items up here, or delete the crawl frontier logic?
            self.crawl_frontier.add(target_url=target_url, referrer_url=async_crawl_task.url)

        # Finally, verify successful execution of task
        self.buffer_queue_entry_completed.append(async_crawl_task.url)

        self.task_durations.append(time.time() - start_time)

    async def run_main_loop(self):

        tasks = []
        while True:

            start_time = time.time()

            crawled_sites = self.resource_database.get_number_of_crawled_sites()
            queued_sites = self.resource_database.get_number_of_queued_urls()
            sites_per_minute = self.calculate_sites_per_minute(crawled_sites)
            average_time_per_task = np.median(self.task_durations)
            proxy_success_rate = self.proxy_list.proxy_list_success_rate
            print("Process {} :: Global Sites per s/m/h: {:.2f}/{:.1f}/{:.1f} -- Crawled sites: {} -- Available proxies: {}".format(self.name, sites_per_minute / 60, sites_per_minute, sites_per_minute * 60, crawled_sites, len(self.proxy_list._proxies.difference(self.proxy_list._proxies_blacklist))))
            print("Process {} :: AVG Time per Task: {:.2f} -- Proxy success rate: {:.1f} -- Queue sites in DB: {}".format(self.name, average_time_per_task, proxy_success_rate, queued_sites))

            print("Populating queue")
            # Populate crawl tasks queue
            urls_to_crawl = self.crawl_frontier.pop_start_list()

            # For all the urls, make sure the markup does not exist yet
            print("Time to populate queue took: ", time.time() - start_time)

            # Let them both run
            # These will never have any outputs, as they both run forever!
            tasks = []
            for url in urls_to_crawl:
                # Spawn a AsyncCrawlTask object
                task = asyncio.create_task(self.task(CrawlAsyncTask(self.proxy_list, url=url)))
                tasks.append(task)

            if tasks:
                await asyncio.gather(*tasks)
                print("Time until gather took: ", time.time() - start_time)

            # "Flush" the database in one go
            print("Flushing records: Markups {} -- Failed {} -- Completed {}".format(len(self.buffer_markup_records), len(self.buffer_queue_entry_failed), len(self.buffer_queue_entry_completed)))
            self.resource_database.create_markup_record(self.buffer_markup_records)
            self.resource_database.get_url_task_queue_record_failed(urls=self.buffer_queue_entry_failed)
            self.resource_database.get_url_task_queue_record_completed(urls=self.buffer_queue_entry_completed)

            # Flush all buffers
            self.flush_buffers()
            self.resource_database.commit()


if __name__ == "__main__":
    print("Starting the application")
    main = Main()

    asyncio.run(main.run_main_loop())
