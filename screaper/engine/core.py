"""
    Run the scrapy web crawler.

    Look at how to make the multiprocessing faster:
    - https://www.cloudcity.io/blog/2019/02/27/things-i-wish-they-told-me-about-multiprocessing-in-python/
"""
import asyncio
import random
import time
from multiprocessing import Process

from screaper.crawl_frontier.crawl_frontier import CrawlFrontier
from screaper_resources.resources.db import Database


class Engine:

    def __init__(self, resource_database, crawl_frontier, downloader):
        # establish a database connection

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


class ThreadedEngine:

    def __init__(self):

        self.resource_database = Database()
        self.crawl_frontier = CrawlFrontier(resource_database=self.resource_database)
        self.downloader = Downloader(resource_database=self.resource_database)

        self.engine = Engine(self.resource_database, self.crawl_frontier, self.downloader)

    def run(self, max_sites=None):

        # TODO: Pop a site from the proxy-list if the proxy is not healthy!
        # Big try-catch around this?
        # It won't help, really
        try:
            self.engine.run(max_sites=max_sites)
        finally:
            # TODO: Disconnect from database
            self.resource_database.session.close()


class Runner:
    """
        Threaded Wrapper around the engine
    """

    def __init__(self):
        self.max_time = 3600 # 3600
        self.number_processes = 2  # 32  # 32  # Number of processes to spawn. Each process will have a different proxy for a long while
        self.ping_interval = 120  # Ping threads every 2 minutes to make sure that the threads are not dead yet

    def run(self):

        # Now do this in a for-loop
        # Create one engine to populate the database
        print("Create one engine to populate the database")

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
                    p = Process(target=ThreadedEngine().run)
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
