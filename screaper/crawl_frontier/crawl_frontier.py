"""
    Implements a crawl frontier
"""
import os
import re
from urllib.parse import urlparse, urljoin

from url_normalize import url_normalize
from w3lib.url import url_query_cleaner, canonicalize_url

import yaml

from flashtext import KeywordProcessor
from dotenv import load_dotenv
from url_parser import get_base_url

load_dotenv()

class CrawlObjectsBuffer():

    def __init__(self):
        self.buffer = set()

    def flush_buffer(self):
        self.buffer = set()

    def add_to_buffer(self, crawl_object):
        assert isinstance(crawl_object, CrawlObject)
        self.buffer.add(crawl_object)

    def calculate_successful(self):
        return len({x for x in self.buffer if not x.not_successful})

    def calculate_failed(self):
        return len({x for x in self.buffer if x.not_successful})

    def calculate_collected_markups(self):
        return len({x for x in self.buffer if x.markup})

    def calculate_total(self):
        return len(self.buffer)

    def get_markups(self):
        pass


class CrawlObject:

    def __init__(self, url, queue_id, depth):

        # Do a bunch of more asserts on the type
        assert url, url
        assert queue_id, queue_id
        assert depth, depth

        # Could probably even make this more string by applying a regex on the url
        assert isinstance(url, str), (url, type(url))
        assert isinstance(queue_id, int), (queue_id, type(queue_id))
        assert isinstance(depth, int), (depth, type(depth))

        self.url = url
        self.queue_id = queue_id
        self.depth = depth

        # Items that will be assigned during the runtime
        self.status_code = None
        self.target_urls = []
        self.markup = None
        self.score = None

        self.not_successful = False
        self.errors = []

    def add_error(self, err):
        self.errors.append(err)
        self.not_successful = True

        self.score = 0

class LinkProcessor:

    def __init__(self):
        self.blacklist = []
        self.whitelist = []

        self.popular_websites = []
        with open(os.getenv("PopularWebsitesYaml"), 'r') as file:
            self.popular_websites = yaml.load(file)["websites"]
            # print("Popular websites are: ", self.popular_websites)

        self.populat_websites_processor = KeywordProcessor()
        self.populat_websites_processor.add_keywords_from_list(self.popular_websites)

        # Later on implement when a website is considered outdated
        self.outdate_timedelta = None
        self.regex = re.compile("(?i)\b((?:(https|https)?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

    def is_absolute(self, url):
        return bool(urlparse(url).netloc)

    def process(self, target_url, referrer_url):
        """
            Adds an item to be scraped to the persistent queue
        """

        # TODO: Add URL normalization here

        # Very hacky now, which is fine
        if target_url is None:
            # TODO: Log a warning that some url is none!
            return
        target_url = target_url.strip()
        # apply whitelisting
        if target_url.strip() == "":
            # if link is empty, it is probably broken, skip
            return
        if target_url[0] == "#":
            # if link starts with "#", skip this (because this is just an anchor
            return
        if target_url[0] == "/":
            # if link starts with slash, then this is a relative link. We append the domain to the url
            basic_url = get_base_url(referrer_url)  # Returns just the main url
            target_url = basic_url + target_url

        if self.is_absolute(target_url):
            basic_url = get_base_url(referrer_url)  # Returns just the main url
            target_url = urljoin(basic_url, target_url)

        # Bring target URL into unified format
        if target_url.endswith('/'):
            target_url = target_url[-1]

        # Finally, apply url_normalization
        target_url = url_normalize(target_url)
        target_url = url_query_cleaner(target_url, parameterlist=['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'], remove=True)
        target_url = canonicalize_url(target_url)

        if target_url.endswith("/"):
            target_url = target_url[:-1]

        target_url = target_url.split('#')[0]

        # TODO: Implement contents to also be parsed and links added

        # Add more cases why one would skip here
        skip = False
        if self.populat_websites_processor.extract_keywords(target_url):
            skip = True

        # Also return these, rather than commiting these immediately
        # (Or just keep them, because we don't read from here anyways...?
        # Do profiling before pushing these up the hierarchy
        return target_url, referrer_url, skip

if __name__ == "__main__":
    print("Check the crawl frontier")
