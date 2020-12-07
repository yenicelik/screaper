"""
    Run the scrapy web crawler
"""
import time

import requests

from screaper.crawl_frontier.crawl_frontier import crawl_frontier
from screaper.downloader.downloader import downloader
from screaper.resources.db import resource_database


class Engine():

    def seed_urls(self):
        return [
            # "https://www.thomasnet.com/browse/",  # entire database
            # "https://www.thomasnet.com/browse/machinery-tools-supplies-1.html",  # category depth 1
            "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html",  # category depth 2
            # "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings/roller-1.html",  # category depth 3
            # "https://www.thomasnet.com/products/roller-bearings-4221206-1.html",  # category listing (with multiple pages)
            # "https://www.thomasnet.com/profile/01150392/bdi.html?cov=NA&what=Roller+Bearings&heading=4221206&cid=1150392&searchpos=1",  # example distributor website
            # "https://www.bdiexpress.com/us/en/",  # example distributor website
        ]

    def __init__(self):
        # establish a database connection
        pass

    def run(self):
        """
            Run the crawler. This will run for many, many hours (up to 80 days, unless parallalized).
            I will try to setup a single docker container.
        :return:
        """

        while True:

            crawled_sites = resource_database.get_number_of_crawled_sites()
            print("Number of crawled sites are: ", crawled_sites)
            if crawled_sites > 10000:
                exit(0)

            # print("Getting from queue")

            # dirty try catch ; should resolve this in a better way
            retries = 0
            queue_obj = None
            while not queue_obj:
                if retries > 5:
                    exit(-1)
                # print("Pop from queue")
                queue_obj = crawl_frontier.pop_start()
                # print("Pop from queue success!")
                if not queue_obj:
                    retries += 1
                    time.sleep(0.1)

            url, referrer_url = queue_obj.url, queue_obj.referrer_url

            # print("Referring url is: ", referrer_url)

            print("Scraping url: ", url)
            if url is None:
                # print("skipping: url is None")
                break

            markup_exists = resource_database.get_markup_exists(url)
            if not markup_exists:

                # Ping the contents of the website
                # print("Retrieving markup")
                markup, response_code = downloader.get(url)
                # print("Markup is: ", markup)

                # If response code is not a 200, put it back into the queue and process it at a later stage again
                if not (response_code == requests.codes.ok):
                    crawl_frontier.pop_failed(url, referrer_url)

                # Add scraped items to the mongodb database:
                # print("Adding to database")
                downloader.add_to_index(url, markup)

                # parse all links from the markup
                # print("Getting urls from markup")
                target_urls = markup_processor.get_links(url, markup)
                # print("target urls: ", target_urls)

                # for each link in the queue, add this to the queue:
                for target_url in target_urls:
                    # print("Adding target url: ", target_url)
                    # print("Adding reference url: ", url)
                    crawl_frontier.add(target_url=target_url, referrer_url=url)
                    # print("Added target url: ", target_url)
                    # print("Adding reference url: ", url)
            else:
                print("Markup already exists!", url)

            crawl_frontier.pop_verify(url, referrer_url)


if __name__ == "__main__":
    print("Starting the engine ...")
