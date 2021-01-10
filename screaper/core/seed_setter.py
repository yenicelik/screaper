"""
    File to set a set of seeds
"""
from screaper.crawl_frontier.crawl_frontier import CrawlFrontier
from screaper_resources.resources.db import Database


class Seed:

    def __init__(self, resource_database, crawl_frontier):
        # establish a database connection

        self.resource_database = resource_database
        self.crawl_frontier = crawl_frontier

        seed_urls = [
            # "https://www.thomasnet.com/browse/",  # entire database
            # "https://www.thomasnet.com/browse/machinery-tools-supplies-1.html",  # category depth 1
            # "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html",  # category depth 2
            # "https://www.thomasnet.com/catalogs/mechanical-components-and-assemblies/bearings/",
            # "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide",
            # "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings/roller-1.html",  # category depth 3
            # "https://www.thomasnet.com/products/roller-bearings-4221206-1.html",  # category listing (with multiple pages)
            # "https://www.thomasnet.com/profile/01150392/bdi.html?cov=NA&what=Roller+Bearings&heading=4221206&cid=1150392&searchpos=1",  # example distributor website
            # "https://www.bdiexpress.com/us/en/",  # example distributor website
            "https://www.dtr-ihk.de/mitgliedschaft/mitgliederverzeichnis",
            "https://www.wlw.ch/",
            # "https://www.europages.com/?__hstc=80469576.14de7e5c17b732441ca7b7db9be17ae3.1610191905892.1610219319699.1610224238499.7&__hssc=80469576.1.1610224238499&__hsfp=105719331",
            "https://www.europages.de/Maschinenbau%20und%20Industrie%20-%20Ausr%C3%BCstungen.html"
        ]

        add_seed_urls = True or (self.resource_database.get_number_of_queued_urls() == 0)
        print("Number of sites: ", self.resource_database.get_number_of_queued_urls(), add_seed_urls)

        # Delete all in URL and other tables

        if add_seed_urls:
            print("Adding seed urls: ")

            for x in seed_urls:
                print("Adding: ", x)
                self.resource_database.create_url_entity(urls=["/"])

                self.resource_database.create_url_entity(urls=[x])
                self.resource_database.create_url_queue_entity(url_skip_score_depth_tuple_dict=dict([(x, (False, 0, 0))]))
                self.resource_database.create_referral_entity(target_url_referrer_url_tuple_list=[(x, "/")])

            self.resource_database.commit()

if __name__ == "__main__":
    print("Adding seed items")

    database = Database()
    crawl_frontier = CrawlFrontier(database)

    seed_generator = Seed(database, crawl_frontier)

