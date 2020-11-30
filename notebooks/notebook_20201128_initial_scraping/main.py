"""
    Scrapes an example final company page from thomasnet
"""

# TODO: Implement some mechanism that checks how many failed requests per second,
# and skips all items in the queue with that domainname

# implement selectiveness
# implement re-visit
# implement politeness
# implement parallelization

# implement website caching (request package?) https://pypi.org/project/requests-cache/

# look at robots.txt and ignore the ones that are not allowed

# sanitize html inputs before putting these into the postgres database: https://w3lib.readthedocs.io/en/latest/w3lib.html
# create an embedded state-representation that determines to look for further selection or not
import time

import requests

from screaper.crawl_frontier.crawl_frontier import crawl_frontier
from screaper.downloader.downloader import downloader
from screaper.engine.markup_processor import markup_processor
from screaper.resources.db import resource_database
from screaper.resources.entities import UrlTaskQueue, Markup

basedir = "/Users/david/screaper/data/"


if __name__ == "__main__":

    # Tools to build: distributor website classification (hand-picked / labelled tools to make sure that this works)

    initial_urls = [
        # "https://www.thomasnet.com/browse/",  # entire database
        # "https://www.thomasnet.com/browse/machinery-tools-supplies-1.html",  # category depth 1
        "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html",  # category depth 2
        # "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings/roller-1.html",  # category depth 3
        # "https://www.thomasnet.com/products/roller-bearings-4221206-1.html",  # category listing (with multiple pages)
        # "https://www.thomasnet.com/profile/01150392/bdi.html?cov=NA&what=Roller+Bearings&heading=4221206&cid=1150392&searchpos=1",  # example distributor website
        # "https://www.bdiexpress.com/us/en/",  # example distributor website
    ]
    # For startup and in case something goes wrong now
    # remove everything from the table
    resource_database.session.query(UrlTaskQueue)
    resource_database.session.query(Markup)

    for x in initial_urls:
        crawl_frontier.add(target_url=x, referrer_url="")

    print("Starting small scraping script")

    # for now, include a certain type of whitelisting

    # TODO: how to identify distributor websites?
    i = 0

    while True:
        i += 1
        print("i is: ", i)
        if i > 5:
            exit(0)

        print("Getting from queue")

        # dirty try catch ; should resolve this in a better way
        retries = 0
        queue_obj = None
        while not queue_obj:
            if retries > 5:
                exit(-1)
            print("Pop from queue")
            queue_obj = crawl_frontier.pop_start()
            print("Pop from queue success!")
            if not queue_obj:
                retries += 1
            time.sleep(1)

        url, referrer_url = queue_obj.url, queue_obj.referrer_url

        print("Scraping url: ", url)
        if url is None:
            print("skipping: url is None")
            break

        # Ping the contents of the website
        print("Retrieving markup")
        markup, response_code = downloader.get(url)
        print("Markup is: ", markup)

        # If response code is not a 200, put it back into the queue and process it at a later stage again
        if not (response_code == requests.codes.ok):
            crawl_frontier.pop_failed(url)

        # Add scraped items to the mongodb database:
        print("Adding to mongodb database")
        downloader.add_to_index(url, referrer_url, markup)

        # parse all links from the markup
        print("Getting urls from markup")
        target_urls = markup_processor.get_links(url, markup)
        print("target urls: ", target_urls)

        crawl_frontier.pop_verify(url)

        # for each link in the queue, add this to the queue:
        for target_url in target_urls:
            print("Adding target url: ", target_url)
            crawl_frontier.add(target_url=target_url, referrer_url=referrer_url)
            print("Added target url: ", target_url)
