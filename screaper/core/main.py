"""
    Includes the main application loop
"""
import asyncio
import time

import requests

from screaper.crawl_frontier.crawl_frontier import CrawlFrontier

from screaper.downloader.async_crawl_task import CrawlAsyncTask
from screaper_resources.resources.db import Database
from screaper_resources.resources.resouces_proxylist import ProxyList


class Main:

    # TODO: Add depth to URLs, s.t. we can apply breadth first search

    def __init__(self):
        # Start the needed resources
        self.proxy_list = ProxyList()
        self.resource_database = Database()  # TODO Make database async!

        self.crawl_frontier = CrawlFrontier(resource_database=self.resource_database)

        # Implement an async-queue

        self.ping_interval = 5  # How many seconds to run the ping interval for

        self.active_workers_count = 0

        self.timestamps = []

    def calculate_sites_per_hour(self, crawled_sites):
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

        sites_per_hour = sites_per_second * 60 * 60

        return sites_per_hour

    async def producer(self, crawl_task_queue):
        """
            Populates the queue with CrawlAsyncTask objects,
            which the consumer can take and then scrape
        :return:
        """

        # Do not produce more items into the queue
        # Single while loop which populates the queue

        while True:

            crawled_sites = self.resource_database.get_number_of_crawled_sites()
            queued_sites = self.resource_database.get_number_of_queued_urls()
            sites_per_hour = self.calculate_sites_per_hour(crawled_sites)
            print("Sites per hour: {} -- Crawled sites: {} -- Queue sites in DB: {} -- Sites in local queue: {}".format(sites_per_hour, crawled_sites, queued_sites, crawl_task_queue.qsize()))
            if crawl_task_queue.qsize() > (crawl_task_queue.maxsize // 2):
                await asyncio.sleep(5)
                continue

            print("Populating queue")
            # Populate crawl tasks queue
            queue_objs_to_crawl = self.crawl_frontier.pop_start_list()

            for queue_obj in queue_objs_to_crawl:
                # Spawn a AsyncCrawlTask object

                # If the markup does not exist yet, spawn a crawl async task
                markup_exists = self.resource_database.get_markup_exists(queue_obj.url)  # TODO make async
                if markup_exists:
                    print("Markup exists", queue_obj.url)
                    # TODO: Make one batched request
                    self.resource_database.get_url_task_queue_record_completed(url=queue_obj.url)
                    self.resource_database.commit()
                if not queue_obj.url:
                    print("URL is None", queue_obj.url)
                    self.resource_database.get_url_task_queue_record_completed(url=queue_obj.url)
                    self.resource_database.commit()
                crawl_async_task = CrawlAsyncTask(self.proxy_list, queue_obj)
                await crawl_task_queue.put(crawl_async_task)

    async def consumer(self, max_sites, crawl_task_queue):
        """
            Consumes the CrawlAsyncTasks produced into the queue above
        :return:
        """

        # Just spawn new threads while the queue is not empty
        c = 0
        while True:

            if isinstance(max_sites, int) and c > max_sites:
                print("Number of maximum crawled sites through this thread done", c, max_sites)
                return

            # Get from queue
            # Consume half the queue
            async_crawl_task = await crawl_task_queue.get()  # This will wait until there is something in the queue anyways!
            status_code, markup, target_urls = await async_crawl_task.fetch()

            # If an error is returned, just skip it:
            if status_code is None:
                # print("Some error happened!")
                self.crawl_frontier.pop_failed(async_crawl_task.queue_obj.url)
                continue
            else:
                # print("Made request to web server and got response", status_code, len(markup), len(target_urls))
                pass

            # Push them into the database
            if not (status_code == requests.codes.ok):
                # print("Not an ok status code!")
                self.crawl_frontier.pop_failed(async_crawl_task.queue_obj.url)
            else:
                # print("Adding to database")
                self.resource_database.add_to_index(async_crawl_task.queue_obj.url, markup)

            for target_url in target_urls:
                self.crawl_frontier.add(target_url=target_url, referrer_url=async_crawl_task.queue_obj.url)

            # Finally, verify successful execution of task
            self.crawl_frontier.pop_verify(async_crawl_task.queue_obj.url)

            # Verify that the queued task is now done
            crawl_task_queue.task_done()

            c += 1

    async def run_main_loop(self):

        crawl_task_queue = asyncio.Queue(maxsize=4096)

        number_consumers = 100

        # 1395

        # Create N (multiple) consumers
        tasks = [self.consumer(max_sites=100, crawl_task_queue=crawl_task_queue) for _ in range(number_consumers)]
        # Create 1 (one) producer
        tasks.append(self.producer(crawl_task_queue=crawl_task_queue))

        print("Consumer and producer tasks are: ", tasks)

        # Let them both run
        # These will never have any outputs, as they both run forever!
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    print("Starting the application")
    main = Main()

    asyncio.run(main.run_main_loop())
