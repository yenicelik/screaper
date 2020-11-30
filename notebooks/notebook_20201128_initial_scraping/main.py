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
from datetime import datetime

import pymongo
import requests
import bleach
from pyquery import PyQuery as pq
from persistqueue import SQLiteQueue
from url_parser import get_base_url

basedir = "/Users/david/screaper/data/"

headers = {
    "User-Agent": "Mozilla/5.0",  # (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)
    "From": "contact@theaicompany.com"
}

crawl_frontier_queue = SQLiteQueue(basedir + "queue", auto_commit=True, multithreading=True)
mongo_client = pymongo.MongoClient("localhost", 27017)
mongo_db = mongo_client["scraped_markups"]
# Set an index
mongo_db.collection.create_index("url")

def retrieve_website_markup(url):
    """
        Returns the markup scraped from the website
    """
    time.sleep(0.5)

    response = requests.get(url, headers=headers)
    print("Response is: ", response)
    content = response.text
    print("content is: ", content)
    content = bleach.clean(content)
    response_code = response.status_code

    return content, response_code


def add_url_to_queue(target_url, referrer_url, queue):
    """
        Adds an item to be scraped to the persistent queue
    """

    queue.put((target_url, referrer_url))

    return queue

def get_from_queue(queue):
    """
        Retrieves the item to work on in the queue
    """
    if len(queue) == 0:
        return None, None

    tpl = queue.get()
    target_url, referrer_url = tpl
    return target_url, referrer_url


# Use MongoDB as an index
def get_urls_from_markup(url, markup):
    """
        Returns a list of all urls within a markup.
        If no url was found,
    """
    out = []

    pyquery_object = pq(markup)
    for link in pyquery_object('a').items():

        print("Link looks as follows: ", link, type(link))
        link = link.attr['href']  # only grab the href attribute

        # if link is empty, it is probably broken, skip
        if link.strip() == "":
            continue
        # if link starts with "#", skip this (because this is just an anchor
        if link.strip()[0] == "#":
            continue
        # if link starts with slash, then this is a relative link. We append the domain to the url
        if link.strip()[0] == "/":
            basic_url = get_base_url(url)  # Returns just the main url
            link = basic_url + link
        # Other ways to check if link is valid?
        # TODO: Implement contents to also be exported

        out.append(link)
        print(link)

    return out

def add_to_mongodb_database(url, referred_url, markup):
    """
        Inserts the required json object into the mongodb

        # create url of following json type
        # referrer
        # datetime fetched
        # markup
        # images ? => let's exclusively focus on text for now
        # url (also used as an index)
        # retries (in case of an unsuccessful try)  # also perhaps later? should perhaps do edge-case mitigation once this issue persists a bit more

        # markup titles (title of the markup from the initial website (?))

    """
    obj = {
        "url": url,
        "referrer_uri": referred_url,
        "markup": markup,
        "datetime_fetched": datetime.now()
    }
    # check if the url is existent:
    insert_id = mongo_db.collection.insert_one(obj).inserted_id

    return insert_id

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
    mongo_db.collection.remove({})  # for now, make this empty
    # for url in initial_urls:
    #     mongo_db.collection.remove({"url": url})
    #     print("All items are now")
    #     print("after removed", mongo_db.collection.find({"url": url}).count())
    for x in initial_urls:
        crawl_frontier_queue.put((x, ".none",))

    print("Starting small scraping script")

    # for now, include a certain type of whitelisting
    whitelist = "https://www.thomasnet.com"

    # TODO: how to identify distributor websites?

    i = 0

    while True:
        i += 1
        print("i is: ", i)
        if i > 5:
            exit(0)

        print("Getting from queue")
        url, referrer_url = get_from_queue(crawl_frontier_queue)
        print("Scraping url: ", url)
        if url is None:
            print("skipping: url is None")
            break
        if mongo_db.collection.find({"url": url}).count() > 0:
            # if URL was crawled before, skip this
            # attention: has a chance of outliers
            # in graph-terms, this prevents circular traversals
            print("skipping: url was already scraped", mongo_db.collection.find({"url": url}).count())
            continue
        if whitelist not in url:
            # if URL is not part of thomasnet, put it to the end of the queue for now (prioritize thomasnet websites)
            print("skipping: url not whitelisted", whitelist)
            add_url_to_queue(url, referrer_url, crawl_frontier_queue)
            continue

        # Ping the contents of the website
        print("Retrieving markup")
        markup, response_code = retrieve_website_markup(url)
        print("Markup is: ", markup)

        # If response code is not a 200, put it back into the queue and process it at a later stage again
        if not (response_code == requests.codes.ok):
            add_url_to_queue(url, referrer_url, crawl_frontier_queue)
            continue

        # Add scraped items to the mongodb database:
        print("Adding to mongodb database")
        add_to_mongodb_database(url, referrer_url, markup)

        # parse all links from the markup
        print("Getting urls from markup")
        target_urls = get_urls_from_markup(url, markup)
        print("target urls: ", target_urls)

        # for each link in the queue, add this to the queue:
        for target_url in target_urls:
            print("Adding target url: ", target_url)
            add_url_to_queue(target_url, referrer_url, crawl_frontier_queue)
            print("Added target url: ", target_url)
