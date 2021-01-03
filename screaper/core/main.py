"""
    Includes the main application loop
"""
import asyncio

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

        self.crawl_task_queue = asyncio.Queue(maxsize=513)
        self.active_workers_count = 0

    def execute_single_task_from_queue(self, max_sites=None):

        # Fetch from queue

        ##############
        # If queue is shallow or empty, populate queue
        ##############

        # Else, run worker
        pass

    async def run_main_loop(self):

        c = 0

        while True:

            # if isinstance(max_sites, int) and c > max_sites:
            #     print("Number of maximum crawled sites through this thread done", c, max_sites)
            #     return

            # Run multiple of the self.execute_single_task_from_queue instances.
            # This will act as if many threads are simultenously running

            # Fetch more items into the queue
            if not crawl_task_queue.full():
                # Fetch from database
                # TODO: Make this
                # Do multiple retries of this, and fail gracefully.
                # Nevermind, there will be multiple retries anyways
                queue_objs_to_crawl = self.crawl_frontier.pop_start_list()
                tasks_to_await = []
                for queue_obj in queue_objs_to_crawl:
                    # TODO: Gotta spawn a coroutine from this here
                    markup_exists = self.resource_database.get_markup_exists(queue_obj.url)  # TODO make async
                    if not markup_exists and queue_obj.url:
                        crawl_task = CrawlAsyncTask(self.proxy_list, queue_obj)
                        # TODO why await
                        crawl_task_queue_put_task = crawl_task_queue.put(crawl_task)
                        tasks_to_await.append(crawl_task_queue_put_task)
                    else:
                        print("Markup already exists", queue_obj.url)
                        # Mark this as processed
                        self.resource_database.get_url_task_queue_record_completed(url=queue_obj.url)
                self.resource_database.commit()

                # Similar to blocking really, but allows for parallellism
                for crawl_task_queue_put_task in tasks_to_await:
                    await crawl_task_queue_put_task

                print("Queue is: ", len(queue_objs_to_crawl), queue_objs_to_crawl)

            tasks_to_await = []
            # Spawn a bunch of async tasks
            for i in range(active_workers_count):
                get_crawl_task = crawl_task_queue.get()
                tasks_to_await.append(get_crawl_task)

            # TODO: Put this in another section where you have to await the entire pipeline?
            for get_crawl_task in tasks_to_await:
                await get_crawl_task
                print("Get crawl task is: ", get_crawl_task)


                # TODO: Does this make sure it gets run like a thread, i.e. in parallel?
                executed_crawl_task = asyncio.run(crawl_task)

                # Put them into the next queue, if they don't return None

                # Complete bullshit pseudocode
                await executed_crawl_task_queue.put(executed_crawl_task)

            exit(0)

            if not crawl_task_queue.empty():
                # Go through all executed tasks, and process them into the database one after the other
                for i in len(executed_crawl_task_queue):

                    executed_crawl_task = await executed_crawl_task_queue.get()
                    status_code, markup, target_urls = executed_crawl_task

                    # If response code is not a 200, put it back into the queue and process it at a later stage again
                    if not (status_code == requests.codes.ok):
                        # TODO: Implement some other way to do error checking
                        print("Not an ok status code!")
                        self.crawl_frontier.pop_failed(executed_crawl_task.queue_obj.url)
                    else:
                        # Add scraped items to the mongodb database:
                        # print("Adding to database")
                        self.resource_database.add_to_index(executed_crawl_task.queue_obj.url, markup)

                        # For all newly found target-urls, add them to the list

                        # for each link in the queue, add this to the queue:
                        for target_url in target_urls:
                            # print("Adding target url: ", target_url)
                            # print("Adding reference url: ", url)
                            self.crawl_frontier.add(target_url=target_url, referrer_url=executed_crawl_task.queue_obj.url)
                            # print("Added target url: ", target_url)
                            # print("Adding reference url: ", url)

                        # TODO: For each item in the queue, pop verify
                        self.crawl_frontier.pop_verify(executed_crawl_task.queue_obj.url)

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

    asyncio.run(main.run_main_loop())
