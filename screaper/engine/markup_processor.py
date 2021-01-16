"""
    Implements a markup processor
"""
import os
import re
from urllib.parse import urlparse, urljoin

import yaml
from dotenv import load_dotenv
from flashtext import KeywordProcessor
from pyquery import PyQuery as pq
from url_normalize import url_normalize
from url_parser import get_base_url
from w3lib.url import url_query_cleaner, canonicalize_url

load_dotenv()


class MarkupProcessor:

    def __init__(self):
        self.regex = re.compile(
            "(?i)\b((?:(https|https)?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

    def find_link_in_fulltext(self, markup):
        return re.findall(self.regex, markup)

    def get_links(self, url, markup):

        out = []

        pyquery_object = pq(markup)
        for link in pyquery_object('a').items():

            # print("Link looks as follows: ", link, type(link))
            link = link.attr['href']  # only grab the href attribute

            if link is None:
                # if link is None, then just skip (for whatever reasons of the website, or the crawler
                continue
            if link.strip() == "":
                # if link is empty, it is probably broken, skip
                continue
            if link.strip()[0] == "#":
                # if link starts with "#", skip this (because this is just an anchor
                continue
            if link.strip()[0] == "/":
                # if link starts with slash, then this is a relative link. We append the domain to the url
                basic_url = get_base_url(url)  # Returns just the main url
                link = basic_url + link

            # Other ways to check if link is valid?
            link = url_normalize(link)

            # Normalize URL to common format
            out.append(link)

        return out


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
        self.popular_websites = set(self.popular_websites)

        # Later on implement when a website is considered outdated
        self.outdate_timedelta = None
        self.regex = re.compile(
            "(?i)\b((?:(https|https)?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

    def is_relative(self, url):
        return bool(urlparse(url).netloc)

    def process(self, target_url, referrer_url):
        """
            Adds an item to be scraped to the persistent queue
        """
        assert target_url or target_url == "", target_url
        assert referrer_url or referrer_url == "", referrer_url

        base_url = urlparse(referrer_url).netloc

        # Very hacky now, which is fine
        if target_url is None:
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

        if self.is_relative(target_url):
            # basic_url = get_base_url(referrer_url)  # Returns just the main url
            target_url = urljoin(base_url, target_url)

        # Bring target URL into unified format
        if target_url.endswith('/'):
            target_url = target_url[:-1]

        # Finally, apply url_normalization
        target_url = url_normalize(target_url)
        target_url = url_query_cleaner(target_url, parameterlist=['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'], remove=True)
        target_url = canonicalize_url(target_url)

        target_url = target_url.split('#')[0]
        # Remove the scheme part (as this will be auto-resolved when the request is sent
        # if target_url[:7] == "http://":
        #     target_url = target_url[7:]
        # elif target_url[:8] == "https://":
        #     target_url = target_url[8:]

        # Add more cases why one would skip here
        skip = False

        # If still not a valid URL, skip:
        if not base_url:
            # print("Not a valid URL!", target_url)
            skip = True

        if self.populat_websites_processor.extract_keywords(target_url):
            # print("Too popular of a website!", target_url)
            skip = True

        # Also return these, rather than commiting these immediately
        # (Or just keep them, because we don't read from here anyways...?
        # Do profiling before pushing these up the hierarchy
        return target_url, referrer_url, skip


markup_processor = MarkupProcessor()
