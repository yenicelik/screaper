"""
    Implements a crawl frontier
"""
import os
from re import search

import yaml

from flashtext import KeywordProcessor
from dotenv import load_dotenv
from url_parser import get_base_url

load_dotenv()


class CrawlFrontier:

    def __init__(self, resource_database):
        self.resource_database = resource_database
        self.blacklist = []
        self.whitelist = [
            # "https://www.thomasnet.com",
            # "https://www.go4worldbusiness.com",
            # "https://www.thomasnet.com/products/roller-bearings-4221206",
            # "https://www.thomasnet.com/products/roller-bearings-4221206"
        ]

        self.popular_websites = []
        with open(os.getenv("PopularWebsitesYaml"), 'r') as file:
            self.popular_websites = yaml.load(file)["websites"]
            # print("Popular websites are: ", self.popular_websites)

        self.populat_websites_processor = KeywordProcessor()
        self.populat_websites_processor.add_keywords_from_list(self.popular_websites)

        # Later on implement when a website is considered outdated
        self.outdate_timedelta = None

    def pop_start_list(self):
        queue_uris, queue_uri_depths = self.resource_database.get_url_task_queue_record_start_list()
        return queue_uris, queue_uri_depths

    def add(self, target_url, referrer_url):
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
        # if "http" not in target_url:
        #     return

        # remove all anchors if existent
        target_url = target_url.split('#')[0]

        # Bring target URL into unified format
        if target_url.endswith('/'):
            target_url = target_url[-1]

        # TODO: Make sure that if https is crawled, then don't recrawl the http (and vica versa)

        # Other ways to check if link is valid?
        # Should already be checked elsewhere!
        # # TODO: Implement contents to also be exported
        # if self.resource_database.get_markup_exists(url=target_url):
        #     # If the url's markup was already crawled, do not ping this again
        #     return

        # Add more cases why one would skip here
        skip = False
        # print("Skipping any: ", [x not in target_url for x in self.whitelist])
        # print("Skipping any: ", any([x not in target_url for x in self.whitelist]))
        # print("Skipping any: ", all([x not in target_url for x in self.whitelist]))
        # if all([x not in target_url for x in self.whitelist]):
        #     # if the link is not whitelisted, do not look for this further
        #     skip = True
        if self.populat_websites_processor.extract_keywords(target_url):
            skip = True

        # Also return these, rather than commiting these immediately
        # (Or just keep them, because we don't read from here anyways...?
        # Do profiling before pushing these up the hierarchy
        return target_url, referrer_url, skip

    # TODO: When getting, always prioritize the thomasnet pages before spanning out!


if __name__ == "__main__":
    print("Check the crawl frontier")
