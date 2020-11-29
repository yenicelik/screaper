"""
    Scrapes an example final company page from thomasnet
"""

import time
from datetime import datetime

import pymongo
import requests
from pyquery import PyQuery as pq
from persistqueue import Queue, SQLiteQueue

basedir = "/Users/david/screaper/data/"

headers = {
    "User-Agent": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
    "From": "contact@theaicompany.com"
}

queue = SQLiteQueue(basedir + "queue", auto_commit=True, multithreading=True)
# queue = Queue(basedir + "queue", autosave=True)
mongo_client = pymongo.MongoClient("localhost", 27017)
mongo_db = mongo_client["scraped_markups"]
# Set an index
mongo_db.collection.create_index("url")

def retrieve_website_markup(url):
    """
        Returns the markup scraped from the website
    """
    time.sleep(1.)

    content = requests.get(url, headers=headers).content

    return content


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
def get_urls_from_markup(markup):
    """
        Returns a list of all urls within a markup.
        If no url was found,
    """
    out = []

    pyquery_object = pq(markup)
    for link in pyquery_object('a').items():
        out.append(link.attr['href'])
        print(link.attr['href'])

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
    insert_id = mongo_db.collection.insert_one(obj).insert_id

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
    for url in initial_urls:
        mongo_db.collection.remove({"url": url})
    for x in initial_urls:
        queue.put((x, ".none",))

    print("Starting small scraping script")

    # for now, include a certain type of whitelisting
    whitelist = "https://www.thomasnet.com"

    i = 0

    while True:
        i += 1
        print("i is: ", i)
        if i > 5:
            exit(0)

        print("Getting from queue")
        url, referrer_url = get_from_queue(queue)
        print("Scraping url: ", url)
        if url is None:
            print("skipping: url is None")
            break
        if mongo_db.collection.find({"url": url}):
            # if URL was crawled before, skip this
            # attention: has a chance of outliers
            print("skipping: url was already scraped", mongo_db.collection.find({"url": url}))
            continue
        if whitelist not in url:
            # if URL is not part of thomasnet, put it to the end of the queue for now (prioritize thomasnet websites)
            print("skipping: url not whitelisted", whitelist)
            add_url_to_queue(url, referrer_url, queue)
            continue

        # Ping the contents of the website
        print("Retrieving markup")
        markup = retrieve_website_markup(url)
        print("Markup is: ", markup)

        # Add scraped items to the mongodb database:
        print("Adding to mongodb database")
        add_to_mongodb_database(url, referrer_url, markup)

        # parse all links from the markup
        print("Getting urls from markup")
        target_urls = get_urls_from_markup(markup)
        print("target urls: ", target_urls)

        # for each link in the queue, add this to the queue:
        for target_url in target_urls:
            print("Adding target url: ", target_url)
            add_url_to_queue(target_url, referrer_url, queue)
            print("Added target url: ", target_url)
