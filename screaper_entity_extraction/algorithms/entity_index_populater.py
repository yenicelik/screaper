"""
    Populates an index based on the tagged NER items
"""
import pandas as pd
from bs4 import BeautifulSoup
from tldextract import tldextract
from url_normalize import url_normalize

from screaper_entity_extraction.scraper.scraper import Scraper
from screaper_resources.resources.db import Database


class EntityIndexPopulator:

    def __init__(self):
        # Establish a database connection
        self.db = Database()
        self.scraper = Scraper()

        self.dev = True

    def generate_index_by_named_entity_recognizer(self):

        # For now, drop all rows if included
        # with self.db.engine.connect() as connection:
        #     connection.execute("DELETE FROM named_entities;")

        # Pull a subset
        df = self.db.get_all_indexed_markups(dev=self.dev)

        # TODO: Replace with only grabbing homepages!

        print(df.head())
        print(df.columns)

        markups = df['markup'].tolist()
        markup_ids = df['markup_id'].tolist()
        urls = df['url'].tolist()

        assert len(urls) == len(markups), (len(urls), len(markups))

        for i in range(len(markups)):
            print("Looking at markup number: ", i)
            url = tldextract.extract(urls[i])
            # if url.subdomain:
            #     base_url = "{}.{}.{}".format(url.subdomain, url.domain, url.suffix)
            # else:
            #     base_url = "{}.{}".format(url.domain, url.suffix)
            print("URL is: ", url)
            markups[i] = self.scraper.process(markups[i], url)

        print("Printing all NERs")
        # Run through the scraper
        for i in range(len(markups)):

            # Go through all "ner" attributes, and collect these
            entity_tuples = []
            soup = markups[i]
            print("Markup: ", i, bool(soup))

            for node in soup():
                if node.has_attr("ner"):
                    print("Ner is: ", node.string, node.attrs['ner'], type(node.attrs['ner']))

                    # Input into url table if not in url table
                    url = url_normalize(node.attrs["href"]) if "href" in node.attrs else None
                    url_obj = self.db.insert_url_entity(url)

                    for ner_pair in eval(node.attrs["ner"]):
                        token, ner_label = ner_pair
                        print("Token and label: ", token, ner_label)
                        entity_type = ner_label.split(" ")[0][2:]
                        if entity_type == "ORG":
                            entity_type = "ORGANIZATION"
                        elif entity_type == "LOC":
                            entity_type = "LOCATION"
                        elif entity_type == "WORK_OF_ART":
                            entity_type = "WORK OF ART"
                        elif entity_type == "FAC":
                            entity_type = "FACILITY"
                        elif entity_type == "FAC":
                            entity_type = "FACILITY"
                        tmp = {
                            "label": token,
                            "entity_type": entity_type,
                            "markup_id": markup_ids[i],
                            "external_link": url_obj.id,
                            "heuristic": "named_entity_recognition_classifier"
                        }
                        entity_tuples.append(tmp)

            print("Entity tuples are: ", entity_tuples)

            # Populate the table
            self.db.add_named_entity_candidate(entity_tuples)
            self.db.commit()

        return entity_tuples

    # TODO: Extract all entities out of the homepage.
    # do a special crawler for the homepage, and associate any email, phone number, and company name with this (title)
    def generate_index_by_homepage_title(self):
        """
            Populate the index by pulling all links that are homepages,
            and that are part of the meta:title or meta:description
            or title tags in <head>
        :return:
        """
        # Each homepage carries a meta title, a title, and/or a meta description tag.
        # Associate these with the link of the website that are created
        # TODO: replace by get_all_indexed_markups
        # Especially the homepage should be associated with the respective company
        df = pd.read_csv("/Users/david/screaper/notebooks/notebooks_20201227_scraped_distributors/dump.csv")
        df = df.dropna()

        markups = df['markup'].tolist()
        markup_ids = df['markup_id'].tolist()
        urls = df['url'].tolist()

        # This is a duplicate operation. Can move this one layer up
        for i in range(len(markups)):
            entity_tuples  = []
            print("Looking at markup number: ", i)
            url = tldextract.extract(urls[i])
            # if url.subdomain:
            #     base_url = "{}.{}.{}".format(url.subdomain, url.domain, url.suffix)
            # else:
            #     base_url = "{}.{}".format(url.domain, url.suffix)
            print("URL is: ", url, urls[i])
            print("markups is: ", markups[i])
            if not markups[i]:
                continue

            markups[i] = BeautifulSoup(markups[i])
            soup = markups[i]

            # Select any meta title, meta description, or title tags
            url = url_normalize(urls[i])
            url_obj = self.db.insert_url_entity(url)

            # Make the homepage selector somewhere further down the pipeline, not here
            # Homepage should be a separate attribute somewhere else
            meta_title_was_found = False
            for node in soup("meta"):
                if "name" not in node.attrs:
                    continue
                if node.attrs["name"] == "title" and "content" in node.attrs and node.attrs["content"]:
                    meta_title_was_found = True
                    tmp = {
                        "label": node.attrs["content"],
                        "entity_type": "OTHER",
                        "markup_id": markup_ids[i],
                        "external_link": url_obj.id,
                        "heuristic": "meta_tag"
                    }
                    entity_tuples.append(tmp)
                elif node.attrs["name"] == "description" and "content" in node.attrs and node.attrs["content"]:
                    tmp = {
                        "label": node.attrs["content"],
                        "entity_type": "OTHER",
                        "markup_id": markup_ids[i],
                        "external_link": url_obj.id,
                        "heuristic": "meta_description"
                    }
                    entity_tuples.append(tmp)

            # Skip the title if meta tag was found for title
            for node in soup("title"):
                if node.string is not None:
                    tmp = {
                        "label": node.string,
                        "entity_type": "OTHER",
                        "markup_id": markup_ids[i],
                        "external_link": url_obj.id,
                        "heuristic": "tag_title"
                    }
                    entity_tuples.append(tmp)

            # Maybe also extract all headers? Maybe not a good idea, however.
            # Maybe extract all table items? Maybe not a good idea, however
            # => we don't want to save all the DOM object separately again.

            print("Entity tuples are: ", entity_tuples)

            # Populate the table
            self.db.add_named_entity_candidate(entity_tuples)
            self.db.commit()


    def generate_index_by_link_contents(self):
        """
            Populate the index by pulling all links and extracting inner strings as their label.
            The idea here is that links describe entities.
        :return:
        """

        # Pull a subset
        df = self.db.get_all_indexed_markups(dev=self.dev)
        print(df.head())
        print(df.columns)

        markups = df['markup'].tolist()
        markup_ids = df['markup_id'].tolist()
        urls = df['url'].tolist()

        assert len(urls) == len(markups), (len(urls), len(markups))

        for i in range(len(markups)):
            print("Looking at markup number: ", i)
            url = tldextract.extract(urls[i])
            # if url.subdomain:
            #     base_url = "{}.{}.{}".format(url.subdomain, url.domain, url.suffix)
            # else:
            #     base_url = "{}.{}".format(url.domain, url.suffix)
            print("URL is: ", url)
            markups[i] = self.scraper.process(markups[i], url)
            soup = markups[i]
            entity_tuples = []

            for node in soup('a'):

                token = node.string
                if not token:
                    continue

                # if "href" not in node.attrs or not node.attrs["href"]:
                #     continue

                # Input into url table if not in url table
                url = url_normalize(node.attrs["href"]) if "href" in node.attrs else None
                url_obj = self.db.insert_url_entity(url)

                tmp = {
                    "label": token,
                    "entity_type": "OTHER",
                    "markup_id": markup_ids[i],
                    "external_link": url_obj.id,
                    "heuristic": "link_classifier"
                }
                entity_tuples.append(tmp)

            print("Entity tuples are: ", entity_tuples)

            # Populate the table
            self.db.add_named_entity_candidate(entity_tuples)
            self.db.commit()

if __name__ == "__main__":
    print("Starting to tag the NER items")

    entity_populator = EntityIndexPopulator()
    # entity_populator.generate_index_by_named_entity_recognizer()
    # entity_populator.generate_index_by_link_contents()
    entity_populator.generate_index_by_homepage_title()
