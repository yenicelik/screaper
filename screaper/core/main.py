"""
    Includes the main application loop
"""
import asyncio
import time

import requests

from screaper.crawl_frontier.crawl_frontier import CrawlFrontier
from screaper.downloader.downloader import Downloader

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
        self.downloader = Downloader(resource_database=self.resource_database, proxy_list=self.proxy_list)

        # Implement an async-queue

        self.ping_interval = 5  # How many seconds to run the ping interval for

    def run_main_loop(self, max_sites=None):

        crawl_task_queue = asyncio.Queue(maxsize=513)
        executed_crawl_task_queue = asyncio.Queue(maxsize=513)
        active_workers_count = 0

        c = 0

        while True:

            ##############
            # Populate queue if queue is not big enough
            ##############

            if isinstance(max_sites, int) and c > max_sites:
                print("Number of maximum crawled sites through this thread done", c, max_sites)
                return

            # Fetch more items into the queue
            if not crawl_task_queue.full():
                # Fetch from database
                # TODO: Make this
                # Do multiple retries of this, and fail gracefully.
                # Nevermind, there will be multiple retries anyways
                queue_objs_to_crawl = self.crawl_frontier.pop_start_list()
                for queue_obj in queue_objs_to_crawl:
                    # TODO: Gotta spawn a coroutine from this here
                    markup_exists = self.resource_database.get_markup_exists(queue_obj.url)  # TODO make async
                    if not markup_exists and queue_obj.url:
                        crawl_task = CrawlAsyncTask(self.proxy_list, queue_obj)
                        crawl_task_queue.put(crawl_task)
                    else:
                        print("Markup already exists", queue_obj.url)
                        # Mark this as processed
                        self.crawl_frontier.pop_verify(queue_obj.url)

            # Spawn a bunch of async tasks
            for i in range(active_workers_count):
                crawl_task = crawl_task_queue.get()
                executed_crawl_task = asyncio.run(crawl_task)

                # Put them in, if they don't return None

                # Complete bullshit pseudocode
                executed_crawl_task_queue.put(executed_crawl_task)

            if not crawl_task_queue.empty():
                # Go through all executed tasks, and process them into the database one after the other
                for executed_crawl_task in executed_crawl_task_queue:

                    response_code = executed_crawl_task

                    # If response code is not a 200, put it back into the queue and process it at a later stage again
                    if not (response_code == requests.codes.ok):
                        # TODO: Implement some other way to do error checking
                        self.crawl_frontier.pop_failed(executed_crawl_task.queue_obj.url)
                    else:
                        # Add scraped items to the mongodb database:
                        # print("Adding to database")
                        self.resource_database.add_to_index(queue_obj.url, markup)

                        # For all newly found target-urls, add them to the list

                        # for each link in the queue, add this to the queue:
                        for target_url in target_urls:
                            # print("Adding target url: ", target_url)
                            # print("Adding reference url: ", url)
                            self.crawl_frontier.add(target_url=target_url, referrer_url=queue_obj.url)
                            # print("Added target url: ", target_url)
                            # print("Adding reference url: ", url)

                        # TODO: For each item in the queue, pop verify
                        self.crawl_frontier.pop_verify(queue_obj.url)


            # Try a couple of times, and crash if this doesn't work
            await asyncio.sleep(self.ping_interval)  #  Replace by asny call

            ##############
            # Spawn AsyncTaskRunners
            ##############
            crawled_sites = self.resource_database.get_number_of_crawled_sites()
            queued_sites = self.resource_database.get_number_of_queued_urls()
            print("Crawled sites: {} -- Queue sites: {}".format(crawled_sites, queued_sites))

            c += 1


if __name__ == "__main__":
    print("Starting the application")
    main = Main()


    main.run_main_loop()
