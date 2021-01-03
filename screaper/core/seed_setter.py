"""
    File to set a set of seeds
"""

class Seed:

    def __init__(self, resource_database, crawl_frontier):
        # establish a database connection

        self.resource_database = resource_database
        self.crawl_frontier = crawl_frontier

        seed_urls = [
            # "https://www.thomasnet.com/browse/",  # entire database
            # "https://www.thomasnet.com/browse/machinery-tools-supplies-1.html",  # category depth 1
            # "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html",  # category depth 2
            "https://www.thomasnet.com/catalogs/mechanical-components-and-assemblies/bearings/",
            "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide",
            # "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings/roller-1.html",  # category depth 3
            # "https://www.thomasnet.com/products/roller-bearings-4221206-1.html",  # category listing (with multiple pages)
            # "https://www.thomasnet.com/profile/01150392/bdi.html?cov=NA&what=Roller+Bearings&heading=4221206&cid=1150392&searchpos=1",  # example distributor website
            # "https://www.bdiexpress.com/us/en/",  # example distributor website
        ]

        add_seed_urls = False or (self.resource_database.get_number_of_queued_urls() == 0)
        print("Number of sites: ", self.resource_database.get_number_of_queued_urls(), add_seed_urls)

        # Delete all in URL and other tables

        if add_seed_urls:
            print("Adding seed urls: ")

            for x in seed_urls:
                print("Adding: ", x)
                self.resource_database.create_url_entity(url="")
                self.crawl_frontier.add(target_url=x, referrer_url="")

            self.resource_database.commit()
