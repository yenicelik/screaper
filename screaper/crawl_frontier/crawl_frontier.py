"""
    Implements a crawl frontier
"""
from url_parser import get_base_url


class CrawlFrontier:

    def __init__(self, resource_database):
        self.resource_database = resource_database
        self.blacklist = []
        self.whitelist = [
            "https://www.thomasnet.com",
            "https://www.thomasnet.com",
            # "https://www.thomasnet.com/products/roller-bearings-4221206",
            # "https://www.thomasnet.com/products/roller-bearings-4221206"
        ]

        # Later on implement when a website is considered outdated
        self.outdate_timedelta = None

    def pop_start(self):
        obj = self.resource_database.get_url_task_queue_record_start()
        self.resource_database.commit()
        return obj

    def pop_verify(self, url):
        self.resource_database.get_url_task_queue_record_completed(url=url)
        self.resource_database.commit()

    def pop_failed(self, url):
        self.resource_database.get_url_task_queue_record_failed(url=url)
        self.resource_database.commit()

    def add(self, target_url, referrer_url):
        """
            Adds an item to be scraped to the persistent queue
        """

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

        # Other ways to check if link is valid?
        # TODO: Implement contents to also be exported
        if self.resource_database.get_markup_exists(url=target_url):
            # If the url's markup was already crawled, do not ping this again
            return

        # Add more cases why one would skip here
        skip = False
        # print("Skipping any: ", [x not in target_url for x in self.whitelist])
        # print("Skipping any: ", any([x not in target_url for x in self.whitelist]))
        # print("Skipping any: ", all([x not in target_url for x in self.whitelist]))
        if all([x not in target_url for x in self.whitelist]):
            # if the link is not whitelisted, do not look for this further
            skip = True

        # Create URL entity
        url_obj = self.resource_database.create_url_entity(url=target_url)

        # Add to queue
        url_queue_obj = self.resource_database.create_url_queue_entity(url_entity_obj=url_obj, skip=skip)

        # Add to graph
        url_referral_obj = self.resource_database.create_referral_entity(url_entity=url_obj, referrer_url=referrer_url)

        # Commit database
        self.resource_database.commit()

    # TODO: When getting, always prioritize the thomasnet pages before spanning out!


if __name__ == "__main__":
    print("Check the crawl frontier")
