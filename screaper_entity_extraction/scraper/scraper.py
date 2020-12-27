"""
    Implements a scraper which processes the downloaded markup.

    Some good scraping resources:
    - https://python.hotexamples.com/examples/BeautifulSoup/BeautifulSoup/recursiveChildGenerator/python-beautifulsoup-recursivechildgenerator-method-examples.html


    # Introduce Document-level features
        - Meta Title of Homepage
        - Meta Description of Homepage

    # Introduce Node-level features
        - Proximity to other Text
        - Proximity to link

    # Start with Document-level features to extract entities, probably easiest

"""
import time

from bs4 import BeautifulSoup, Comment, Doctype

from screaper_resources.microservices.language_model_ner import MicroserviceNER
from screaper_entity_extraction.scraper.functional.entity_extraction import extract_entities
from screaper_entity_extraction.scraper.functional.flatten_tree import unwrap_span
from screaper_entity_extraction.scraper.functional.improve_links import improve_links
from screaper_entity_extraction.scraper.functional.remove_attributes import remove_attributes
from screaper_entity_extraction.scraper.functional.remove_tags import remove_tags


class Scraper:

    def __init__(self):
        self.attribute_blacklist = {
            'lang', 'language', 'onmouseover', 'onmouseout', 'script', 'style',
            'font', 'dir', 'face', 'size', 'color', 'style', 'class', 'width',
            'height', 'hspace', 'border', 'valign', 'align', 'background', 'bgcolor',
            'text', 'link', 'vlink', 'alink', 'cellpadding', 'cellspacing', 'data-cert_id',
            'type'
            # added newly
            'src', 'target'
        }

        # Extent whitelist with any additional items that may be useful for future usage!!!
        self.attribute_whitelist = {
            "href", "title", "summary",
            "cols", "colspan", "rows", "rowspan", "content",
            "data", "datetime", "label", "list", "srcdoc", 'description',
            "name"

            # "value",
            # "data-content",
        }

        # self.nlp = spacy.load("xx_ent_wiki_sm")
        self.model_ner = MicroserviceNER()

    # def rename_normalize_tags(self, soup):
    #     """
    #         Rename all tags to some common ones,
    #         decide on a few tags to keep
    #         (lists, buttons)
    #     :param soup:
    #     :return:
    #     """
    #     # Rename all to div for now
    #     tags = soup.find('body').findChildren(recursive=False)
    #     for tag in tags:
    #         if tag.name != "html" and tag.name != "body" and tag.name != "head":
    #             tag.name = 'div'
    #
    #
    # def tag_entities(self, soup):
    #     """
    #         Marks entities as found.
    #         These can be:
    #         - Apply named entity recognition, and filter for
    #         - (1) part-names
    #         - (2) company names
    #         - (3) locations
    #         - (4) (times?)
    #         - (5) links
    #     :return:
    #     """
    #     for tag in soup():
    #         if tag.string:
    #             # Find entities in string
    #             doc = self.nlp(str(tag.string))
    #             print("Document is: ", str(tag.string))
    #             for ent in doc.ents:
    #                 print("Found entities!")
    #                 print(ent.text, ent.start_char, ent.end_char, ent.label_)

    def process(self, html, base_url):

        print("Starting single server scraping")
        time1 = time.time()

        soup = BeautifulSoup(str(html), 'lxml')
        print("Time 1: ", time.time() - time1)

        # TODO: The items inside <a> s are ignored?
        # <h2 class="profile-card__title"><a href="/branchloc.html?act=S&amp;cert=29&amp;cid=10083421&amp;cov=NA&amp;goto=%2Fprofile%2F10083421%2Feconopak.html&amp;heading=97010359&amp;navsource=gnb&amp;searchpos=1" rel="nofollow">Econo-Pak</a></h2><span class="supplier-badge--mobile-icon supplier-badge supplier-badge--verified" data-placement="bottom" data-toggle="tooltip" title="This supplierâs location, business information, and complete products/services have been validated.">
        # TODO: Divide and conquer by commenting out some of the below functions

        # TODO: There is probably a much more efficient implementation for all the require ops
        remove_tags(soup)
        print("Time 2: ", time.time() - time1)

        # img can include href tags.
        # if img does not includes href tag, remove this

        # slightly optional
        for element in soup(text=lambda it: isinstance(it, Comment)):
            element.extract()

        for x in soup.find_all(attrs={"name": "google-site-verification"}):
            x.decompose()

        print("Time 3: ", time.time() - time1)

        # Apply whitelist of attributes
        # Check if whitelist misses anything super-important!
        remove_attributes(soup=soup, whitelist=self.attribute_whitelist, blacklist=self.attribute_blacklist)

        for item in soup.contents:
            print("Iterating through contents: ", item)
            if isinstance(item, Doctype):
                print("Yes!")
                item.extract()

        print("Time 4: ", time.time() - time1)

        # TODO: Pop nodes that have only a single child and parent, and not content or attributes
        improve_links(soup, base_url)

        print("Time 5: ", time.time() - time1)

        # Iteratively remove all tags that have no content (empty tags)

        # Recursively pass the tree, and delete all leaf nodes that are empty
        # in-order-traversal

        # apply NER; and discard all nodes that do not include a NER component
        # Generator should be run in reverse (in-order-traversal)

        # TODO: Only keep NERs

        # self.remove_empty_nodes(soup)  # not quite the right approach to things
        unwrap_span(soup)

        print("Time 6: ", time.time() - time1)

        # rename all the tags into the name "div"
        # self.rename_normalize_tags(soup)

        # self.tag_entities(soup)

        # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nSoup before prettify: \n\n\n\n\n\n\n\n\n\n")
        # print(soup.prettify())

        extract_entities(soup, model_ner=self.model_ner)
        print("Time 7: ", time.time() - time1)


        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nSoup after prettify: \n\n\n\n\n\n\n\n\n\n")
        print(soup.prettify())
        print("Time 8: ", time.time() - time1)

        # soup = soup.prettify()

        # Apply named entity recognition, and filter for
        # (1) partnames
        # (2) company names
        # (3) locations
        # (4) (times?)
        # (5) links

        # bonus items are (more difficult to extract)
        # (1) (company descriptions)

        return soup
