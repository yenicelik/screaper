"""
    Run the scrapy web crawler.

    Look at how to make the multiprocessing faster:
    - https://www.cloudcity.io/blog/2019/02/27/things-i-wish-they-told-me-about-multiprocessing-in-python/
"""
import time
from concurrent.futures.thread import ThreadPoolExecutor
from gc import garbage
from multiprocessing.pool import Pool
from threading import Thread
from multiprocessing import Process

import requests
from requests import ConnectTimeout
from requests.exceptions import ProxyError

from screaper.crawl_frontier.crawl_frontier import CrawlFrontier
from screaper.downloader.downloader import Downloader
from screaper.engine.markup_processor import markup_processor
from screaper_resources.resources.db import Database


class Engine:

    def __init__(self, resource_database, crawl_frontier, downloader):
        # establish a database connection
        self.resource_database = resource_database  # Database()
        self.crawl_frontier = crawl_frontier  # CrawlFrontier(resource_database=self.resource_database)
        self.downloader = downloader  # Downloader(resource_database=self.resource_database)

        seed_urls = [
            # "https://www.thomasnet.com/browse/",  # entire database
            # "https://www.thomasnet.com/browse/machinery-tools-supplies-1.html",  # category depth 1
            # "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html",  # category depth 2
            "https://www.thomasnet.com/catalogs/mechanical-components-and-assemblies/bearings/",
            "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide",
            # "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings/roller-1.html",  # category depth 3
            # "https://www.thomasnet.com/products/roller-bearings-4221206-1.html",  # category listing (with multiple pages)
            # "https://www.thomasnet.com/profile/01150392/bdi.html?cov=NA&what=Roller+Bearings&heading=4221206&cid=1150392&searchpos=1",  # example distributor website
            # "https://www.bdiexpress.com/us/en/",  # example distributor website
        ]

        add_seed_urls = False or (self.resource_database.get_number_of_queued_urls() == 0)
        print("Number of sites: ", self.resource_database.get_number_of_queued_urls(), add_seed_urls)

        # Delete all in URL and other tables

        if add_seed_urls:
            print("Adding seed urls: ")

            for x in seed_urls:
                print("Adding: ", x)
                self.resource_database.create_url_entity(url="")
                self.crawl_frontier.add(target_url=x, referrer_url="")

            self.resource_database.commit()

    def run(self, max_sites=None):
        """
            Run the crawler. This will run for many, many hours (up to 80 days, unless parallalized).
            I will try to setup a single docker container.
        :return:
        """

        c = 0

        while True:

            c += 1

            crawled_sites = self.resource_database.get_number_of_crawled_sites()
            print("Number of crawled sites are: ", crawled_sites)
            if isinstance(max_sites, int) and c > max_sites:
                print("Number of maximum crawled sites through this thread done", c, max_sites)
                return

            # print("Getting from queue")

            # dirty try catch ; should resolve this in a better way
            retries = 0
            queue_obj = None
            while not queue_obj:
                if retries > 5:
                    exit(-1)
                # print("Pop from queue")
                queue_obj = self.crawl_frontier.pop_start()
                # print("Pop from queue success!")
                if not queue_obj:
                    retries += 1
                    time.sleep(0.1)

            # print("Referring url is: ", referrer_url)

            print("Scraping url: ", queue_obj.url)
            if queue_obj.url is None:
                # print("skipping: url is None")
                break

            markup_exists = self.resource_database.get_markup_exists(queue_obj.url)
            if not markup_exists:

                # Ping the contents of the website
                try:
                    markup, response_code = self.downloader.get(queue_obj.url)
                except ProxyError as e:
                    print("Connection Timeout Exception 1!", e)
                    self.downloader.set_proxy()
                    self.crawl_frontier.pop_failed(queue_obj.url)
                    continue
                except ConnectTimeout as e:
                    print("Connection Timeout Exception 2!", e)
                    self.downloader.set_proxy()
                    self.crawl_frontier.pop_failed(queue_obj.url)
                    continue
                except Exception as e:
                    print("Encountered exception: ", e)
                    self.crawl_frontier.pop_failed(queue_obj.url)
                    continue

                # If response code is not a 200, put it back into the queue and process it at a later stage again
                if not (response_code == requests.codes.ok):
                    self.crawl_frontier.pop_failed(queue_obj.url)

                # Add scraped items to the mongodb database:
                # print("Adding to database")
                self.downloader.add_to_index(queue_obj.url, markup)

                # parse all links from the markup
                # print("Getting urls from markup")
                target_urls = markup_processor.get_links(queue_obj.url, markup)
                # print("target urls: ", target_urls)

                # for each link in the queue, add this to the queue:
                for target_url in target_urls:
                    # print("Adding target url: ", target_url)
                    # print("Adding reference url: ", url)
                    self.crawl_frontier.add(target_url=target_url, referrer_url=queue_obj.url)
                    # print("Added target url: ", target_url)
                    # print("Adding reference url: ", url)
            else:
                print("Markup already exists!", queue_obj.url)

            self.crawl_frontier.pop_verify(queue_obj.url)

            # TODO: Put a signal when some time has passed?

class ThreadedEngine(Thread):

    def __init__(self):
        Thread.__init__(self)

        self.resource_database = Database()
        self.crawl_frontier = CrawlFrontier(resource_database=self.resource_database)
        self.downloader = Downloader(resource_database=self.resource_database)

        self.engine = Engine(self.resource_database, self.crawl_frontier, self.downloader)

    def run(self, max_sites=None):

        # Big try-catch around this?
        # It won't help, really
        try:
            self.engine.run(max_sites=max_sites)
        finally:
            # TODO: Disconnect from database
            self.resource_database.session.close()

# TODO: Implement some sort of multithreading inside a pool?
# Each process could have a threadpool

# Spawn a threadpool
def spawn_threadpool(max_number_threads=8, max_time=3600):

    threads = dict()

    # Spawn additional processes if there are not enough processes
    # Just create a Threadpool and let them run within the ThreadPool

    # with ThreadPoolExecutor(max_workers=max_number_threads) as executor:
    #     future = executor.submit(ThreadedEngine().run, 323, 1235)
    #     print(future.result())

    print("Threads in pool are: ", max_number_threads)
    print("Length is: ", max_number_threads - len(threads))
    for i in range(max_number_threads - len(threads)):

        t = ThreadedEngine()
        t.daemon = False
        time.sleep(0.3)
        t.start()
        start_time = time.time()
        name = str(t.name)  # + str(t.get_ident())
        print("Spawning thread nr: {} name: {} len: {} at: {}".format(i, name, len(threads), start_time))

        # threads[name] = {
        #     "thread": t,
        #     "time": start_time
        # }

    print("Sleeping..")

    time.sleep(max_time)
    t.resource_database.close()


class Runner:
    """
        Threaded Wrapper around the engine
    """

    def __init__(self):
        self.max_time = 3600 # 3600
        self.number_processes = 4  # 32  # 32  # Number of processes to spawn. Each process will have a different proxy for a long while
        self.ping_interval = 120  # Ping threads every 2 minutes to make sure that the threads are not dead yet
        self.threads_per_pool = 2

    def run(self):

        # Now do this in a for-loop
        # Create one engine to populate the database
        print("Create one engine to populate the database")
        # close the pool every few hours
        # try:
        #
        #     p = None
        #     start_time = time.time()
        #
        #     while True:
        #
        #         if p is None:
        #             start_time = time.time()
        #             # Create a multiprocessing pool,
        #             p = Pool(self.number_processes)
        #             pool_output = p.apply_async(spawn_threadpool, [self.threads_per_pool,]*(self.number_processes) )
        #             print("Pool output is: ", pool_output)
        #         elif self.max_time < int(time.time() - start_time):
        #             print("Time to live for pools is exceeded! Terminating pool!", self.max_time, int(time.time() - start_time))
        #             p.terminate()
        #             p = None
        #             # Call garbage collect
        #             garbage.collect()
        #
        #         print("Sleep unitl next ping...")
        #         time.sleep(self.ping_interval)
        #
        # finally:
        #     p.terminate()
        #     del p

        # Now do this in a for-loop
        processes = dict()

        # Create one engine to populate the database
        print("Create one engine to populate the database")
        # TODO: The start is buggy
        ThreadedEngine().run(max_sites=1)

        try:

            while True:

                # Spawn additional processes if there are not enough processes
                for i in range(self.number_processes - len(processes)):
                    p = Process(target=spawn_threadpool, args=(self.threads_per_pool, self.max_time))
                    time.sleep(0.3)
                    p.start()
                    start_time = time.time()
                    # a bit disgusting, but that's fine
                    name = str(p.name) + str(p._identity)
                    print("Spawning process pool nr: {} name: {} len: {}".format(i, name, len(processes)))
                    processes[name] = {
                        "process": p,
                        "time": start_time
                    }

                print("Sleep until next Ping...")
                time.sleep(self.ping_interval)

                # Kill any process that has been alive for too long
                tokill = set()

                for name, proc_obj in processes.items():
                    proc = proc_obj["process"]
                    proc_time = proc_obj["time"]

                    # Try to join with a timeout
                    # proc.join(timeout=0)
                    if (time.time() - proc_time) > self.max_time:
                        print("Time is: ", (time.time() - proc_time), self.max_time, (time.time() - proc_time) > self.max_time)
                        print("Process {} will now be terminated".format(name))
                        tokill.add(name)
                    elif proc.is_alive():
                        print("Job is not finished!")
                    else:
                        print("Process {} is dead.".format(name))
                        tokill.add(name)

                for proc_name in tokill:
                    processes[proc_name]['process'].terminate()
                    del processes[proc_name]

        finally:
            for name, proc_obj in processes.items():
                proc_obj['process'].terminate()


engine = Runner()

if __name__ == "__main__":
    print("Starting the engine ...")
    # engine = Engine()
    # engine.run()

    engine_wrapper = Runner()
    engine_wrapper.run()
