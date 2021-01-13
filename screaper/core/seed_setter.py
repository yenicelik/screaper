"""
    File to set a set of seeds
"""
from screaper.crawl_frontier.crawl_frontier import CrawlNextObject
from screaper_resources.resources.db import Database
from screaper_resources.resources.entities import URLEntity


class SeedSetter:

    def __init__(self, resource_database, seed_urls=None):
        # establish a database connection

        self.resource_database = resource_database

        _seed_urls = [
            # "https://www.thomasnet.com/browse/",  # entire database
            # "https://www.thomasnet.com/browse/machinery-tools-supplies-1.html",  # category depth 1
            "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings-1.html",  # category depth 2
            # "https://www.thomasnet.com/catalogs/mechanical-components-and-assemblies/bearings/",
            "https://www.go4worldbusiness.com/suppliers/bearing.html?region=worldwide",
            # "https://www.thomasnet.com/browse/machinery-tools-supplies/bearings/roller-1.html",  # category depth 3
            # "https://www.thomasnet.com/products/roller-bearings-4221206-1.html",  # category listing (with multiple pages)
            # "https://www.thomasnet.com/profile/01150392/bdi.html?cov=NA&what=Roller+Bearings&heading=4221206&cid=1150392&searchpos=1",  # example distributor website
            # "https://www.bdiexpress.com/us/en/",  # example distributor website
            "https://www.dtr-ihk.de/mitgliedschaft/mitgliederverzeichnis",
            "https://www.wlw.ch/",
            # "https://www.europages.com/?__hstc=80469576.14de7e5c17b732441ca7b7db9be17ae3.1610191905892.1610219319699.1610224238499.7&__hssc=80469576.1.1610224238499&__hsfp=105719331",
            "https://www.europages.de/Maschinenbau%20und%20Industrie%20-%20Ausr%C3%BCstungen.html"
        ]
        if seed_urls is None:
            seed_urls = _seed_urls

        print("Seed urls are: ", seed_urls)

        add_seed_urls = True or (self.resource_database.get_number_of_queued_urls() == 0)
        print("Number of sites: ", self.resource_database.get_number_of_queued_urls(), add_seed_urls)

        # Delete all in URL and other tables

        if add_seed_urls:
            print("Adding seed urls: ")

            for x in seed_urls:
                print("Adding: ", x)

                missing = self.resource_database.get_url_entity_not_inserted(urls=[""])
                if missing:
                    print("Missing is: ", missing)
                    self.resource_database.insert_url_entity(urls=[""])
                    self.resource_database.commit()

            for x in seed_urls:
                print("Adding: ", x)

                missing = self.resource_database.get_url_entity_not_inserted(urls=[x])
                if missing:
                    print("Missing is: ", missing)
                    self.resource_database.insert_url_entity(urls=[x])
                    self.resource_database.commit()

            for x in seed_urls:
                print("Adding: ", x)

                crawl_next_objects = [CrawlNextObject(original_url="", target_url=x, skip=False, depth=0, score=0)]

                _, missing = self.resource_database.get_url_queue_inserted_and_missing([x.target_url for x in crawl_next_objects])
                if missing:
                    print("Missing is: ", missing)
                    self.resource_database.insert_missing_queue_items(crawl_next_objects)
                    self.resource_database.commit()

            for x in seed_urls:
                print("Adding: ", x)

                crawl_next_objects = [CrawlNextObject(original_url="", target_url=x, skip=False, depth=0, score=0)]

                # Need to convert this to url ids first
                not_inserted = self.resource_database.get_duplicate_referral_pairs(crawl_next_objects)

                if not_inserted:
                    print("Not inserted is: ", not_inserted)
                    from_id = self.resource_database.session.query(URLEntity.id).filter(URLEntity.url == "").one_or_none()
                    to_id = self.resource_database.session.query(URLEntity.id).filter(URLEntity.url == x).one_or_none()

                    adjacency_tuples = [(to_id, from_id), ]
                    self.resource_database.insert_referral_entity(adjacency_tuples)
                    self.resource_database.commit()


if __name__ == "__main__":
    print("Adding seed items")

    database = Database()
    seed_generator = SeedSetter(database)

