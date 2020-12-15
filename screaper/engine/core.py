"""
    Run the scrapy web crawler
"""
import time

import requests
from requests import ConnectTimeout
from requests.exceptions import ProxyError

from screaper.crawl_frontier.crawl_frontier import crawl_frontier
from screaper.downloader.downloader import downloader
from screaper.engine.markup_processor import markup_processor
from screaper.resources.db import resource_database
from screaper.resources.entities import URLEntity, URLQueueEntity, RawMarkup, URLReferralsEntity

class Engine:

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

        self.add_seed_urls = False or (resource_database.get_number_of_crawled_sites() == 0)

        # Delete all in URL and other tables

        if self.add_seed_urls:

            # resource_database.session.query(URLQueueEntity).delete()
            # resource_database.session.query(URLReferralsEntity).delete()
            # resource_database.session.query(RawMarkup).delete()
            # resource_database.session.query(URLEntity).delete()

            for x in self.seed_urls():
                print("Adding: ", x)
                resource_database.create_url_entity(url="")
                crawl_frontier.add(target_url=x, referrer_url="")

            resource_database.commit()

    def run(self):
        """
            Run the crawler. This will run for many, many hours (up to 80 days, unless parallalized).
            I will try to setup a single docker container.
        :return:
        """

        while True:

            crawled_sites = resource_database.get_number_of_crawled_sites()
            print("Number of crawled sites are: ", crawled_sites)
            if crawled_sites > 40:
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

            # print("Referring url is: ", referrer_url)

            print("Scraping url: ", queue_obj.url)
            if queue_obj.url is None:
                # print("skipping: url is None")
                break

            markup_exists = resource_database.get_markup_exists(queue_obj.url)
            if not markup_exists:

                # Ping the contents of the website
                try:
                    markup, response_code = downloader.get(queue_obj.url)
                except ProxyError as e:
                    print("Connection Timeout Exception 1!", e)
                    downloader.set_proxy()
                    crawl_frontier.pop_failed(queue_obj.url)
                    continue
                except ConnectTimeout as e:
                    print("Connection Timeout Exception 2!", e)
                    downloader.set_proxy()
                    crawl_frontier.pop_failed(queue_obj.url)
                    continue
                except Exception as e:
                    print("Encountered exception: ", e)
                    crawl_frontier.pop_failed(queue_obj.url)
                    continue

                # If response code is not a 200, put it back into the queue and process it at a later stage again
                if not (response_code == requests.codes.ok):
                    crawl_frontier.pop_failed(queue_obj.url)

                # Add scraped items to the mongodb database:
                # print("Adding to database")
                downloader.add_to_index(queue_obj.url, markup)

                # parse all links from the markup
                # print("Getting urls from markup")
                target_urls = markup_processor.get_links(queue_obj.url, markup)
                # print("target urls: ", target_urls)

                # for each link in the queue, add this to the queue:
                for target_url in target_urls:
                    # print("Adding target url: ", target_url)
                    # print("Adding reference url: ", url)
                    crawl_frontier.add(target_url=target_url, referrer_url=queue_obj.url)
                    # print("Added target url: ", target_url)
                    # print("Adding reference url: ", url)
            else:
                print("Markup already exists!", queue_obj.url)

            crawl_frontier.pop_verify(queue_obj.url)


if __name__ == "__main__":
    print("Starting the engine ...")
    engine = Engine()

    engine.run()
