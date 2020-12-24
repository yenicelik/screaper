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
import re
import time

import tldextract
from bs4 import BeautifulSoup, Comment, Doctype

# fout.write(re.sub('\s+', ' ', line))

# TODO: Return triplets that describe a sparse graph ?
from screaper.microservices.language_model_ner import MicroserviceNER


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

    def remove_tag(self, soup, tag_name):
        for x in soup.find_all(tag_name):
            x.decompose()

    def remove_tags(self, soup):
        # These tags should not be removed per-se, but just unwrapped.
        # The underlying items should be pushed up,
        # the tags should be replaced by "divs", so to speak
        # Pose this as an optimization problem if we label end-to-end
        tags = [
            "script",
            "style",
            "svg",
            "link",
            "br"
            # "noscript",
            # "footer",
            # "form",
            # "button",
            # "input"  # This one is needed!
            # "class",
            # slightly optional
            # "select",
            # "header"
        ]
        for x in soup.find_all(tags):
            x.decompose()

    def remove_attributes(self, soup):
        whitelist = True
        if whitelist:
            print("Whitelisting attributes")
            for s in soup.find_all():
                print("Attributes are: ", s.attrs)
                del_attr = set()
                for attr in s.attrs:
                    print("Attr is: ", attr)
                    if attr not in self.attribute_whitelist:
                        print("Popping: ", attr)
                        del_attr.add(attr)
                for x in del_attr:
                    s.attrs.pop(x)
        else:
            print("Deleting attributes")
            for s in soup.find_all():
                print("Attributes are: ", s.attrs)
                del_attr = set()
                for attr in s.attrs:
                    print("Attr is: ", attr)
                    if attr in self.attribute_blacklist:
                        print("Popping: ", attr)
                        del_attr.add(attr)
                for x in del_attr:
                    s.attrs.pop(x)

    def improve_links(self, soup, base_url):
        for link in soup.find_all('a'):

            if 'href' not in link.attrs:
                # What to do in this case?
                continue

            url = link.attrs['href'].strip()

            if url is None:
                # TODO: Log a warning that some url is none!
                # Pop the href attribute
                # TODO: Remove link if not existent
                link.attrs.pop('href')
                continue
            # apply whitelisting
            if url == "":
                # if link is empty, it is probably broken, skip
                link.attrs.pop('href')
                continue
            if url[0] == "#":
                # if link starts with "#", skip this (because this is just an anchor
                # I'm going to be aggressive here
                link.attrs.pop('href')
                continue
            if len(url) >= 10 and url[:10] == "javascript":
                # pop the url
                print("Detected javascript!", url)
                link.attrs.pop('href')
                continue
            if url[:6] == "tel://":
                # Maybe don't skip, but find phone-number from this ...?
                print("Detected tel, skipping!", url)
                link.attrs.pop('href')
                continue

            if url[0] == "/":
                # if link starts with slash, then this is a relative link. We append the domain to the url
                if not base_url.subdomain:
                    url = "http://{}.{}".format(base_url.domain, base_url.suffix) + url
                    link.attrs['href'] = url
                else:
                    url = "http://{}.{}.{}".format(base_url.subdomain, base_url.domain, base_url.suffix) + url
                    link.attrs['href'] = url
                # TODO: Does this destroy the inner contents???
            elif url[:4] != "http" and ":" not in url:
                print("Detected no http!", url)
                if not base_url.subdomain:
                    url = "http://{}.{}".format(base_url.domain, base_url.suffix) + "/" + url
                    link.attrs['href'] = url
                else:
                    url = "http://{}.{}.{}".format(base_url.subdomain, base_url.domain, base_url.suffix) + "/" + url            # else:
                    link.attrs['href'] = url

                    # Mark the link as an external link:
            print("External url?", tldextract.extract(url).domain != base_url.domain,
                  tldextract.extract(url).domain, base_url.domain, type(tldextract.extract(url).domain), type(base_url.domain))
            if tldextract.extract(url).domain != base_url.domain:
                link.attrs["external_link"] = "True"
            else:
                link.attrs["external_link"] = "False"


    def remove_empty_nodes(self, soup):
        """
            CURRENTLY NOT USED!!!
        :param soup:
        :return:
        """
        remove_redundant = True
        if remove_redundant:
            # Iterate each line
            for x in soup.find_all():

                # fetching text from tag and remove whitespaces
                # Empty attributes!
                # print("x is: ", x.get_text().replace("\n", " ").strip())
                # print("x is: ", len(x.get_text().replace("\n", " ").strip()))

                # Also check if there's any children (unless we do in-order node traversal
                # Actually, this should be correct, bcs get text gets the text collectively

                # TODO: But then we must check if any child nodes have any attributes!!
                # We can

                # TODO: Does this include text for all childs as well?
                if len(x.get_text().replace("\n", " ").strip()) == 0:
                    if x.attrs is None:
                        print("Deleting: ", x, x.get_text, x.attrs)
                        x.decompose()
                    elif len(x.attrs) == 0:
                        # Remove empty tag
                        print("Deleting: ", x, x.get_text, x.attrs)
                        x.decompose()

                print("x attrs: ", x.attrs)

                if x.attrs is not None:
                    print("x attrs: ", len(x.attrs))

    def extract_entities(self, soup):

        for x in soup():

            # TODO: Implement NER
            if x.string is None:
                continue

            query = x.string.split(".")
            query = [x for x in query if x]
            if not query:
                continue

            sentences, named_entities = self.model_ner.predict(query=query)

            # -> TODO: This is going to be very lossy!!!
            # -> But this is fine
            # TODO: Also keep if a link is nearby

            # Check if all are Os
            if all([x == "O" for named_entity in named_entities for x in named_entity]):
                print("Should delete this string: ")
                print(x.string)
                # Do not look further
                # Do not delete if external link:
                if not ("www." or ".com" in x.string):
                    x.string = ""
                continue

            out = []

            # iterate over each sentence
            for sentence, named_entity in zip(sentences, named_entities):

                # Extract the named entities, and add them as an attribute
                if all([x == "O" for x in named_entity]):
                    # Replace the string with an empty string
                    # We still keep the string, as this may be useful for contextual word embeddings
                    continue

                # TODO: Add named entities as an attribute
                # Can process this later?
                # Maybe also add to the database as a named entity
                # Or add it at a later stage?
                # TODO: Continue here
                # Will this be fast enough? I think not... :/
                # Perhaps use Google instead. But that's gonna be expensive
                # Merge multiple entities, and create a list of such entities.
                # You can then save such named entities
                a = 0
                b = 0
                start = False
                finish = False
                # Account for the case: ['B-ORG', 'I-ORG'] 0
                # TODO: I forgot the fact that there could be multiple entities!!!
                for i in range(len(named_entity)):

                    # TODO: Write some unittests for this portion

                    # Identify Named Entity
                    if "B-" in named_entity[i]:
                        print("Found named entity: ", named_entity, sentence, i)

                        # Skip if not a useful entity?
                        if named_entity[i] in ("B-LAW", "B-PERCENT", "B-ORDINAL"):
                            continue

                        start = True
                        finish = False
                        a = i

                    # Finish Named Entity
                    elif "I-" in named_entity[i]:
                        print("Continue named entity: ", named_entity, i)

                    elif start and "O" == named_entity[i]:
                        print("Partial named entity: ", named_entity, i)
                        b = i
                        start = False
                        finish = True

                    elif start and i == len(named_entity) - 1:
                        # Reached the end of the named entity list
                        print("Full named entity: ", named_entity, i)
                        b = None  # i
                        start = False
                        finish = True

                    elif start and "B-" in named_entity[i+1]:
                        # above case rules out that i+1 >= len(named_entity)
                        print("Continue named entity: ", named_entity, i)
                        b = i + 1
                        start = False
                        finish = True

                    if (not start) and finish:
                        entity_pair = (" ".join(sentence[a:b]), " ".join(named_entity[a:b]))
                        print("Appending entity pair: ", entity_pair, a, b)
                        out.append(entity_pair)
                        start = False
                        finish = False

            if out:
                print("Appending entity pair: ", out)
                x.attrs["ner"] = str(out)

        # TODO: Remove unnecessary nodes and unwrap even further
        # Perhaps just be aggressive and see how it works
        for x in reversed(soup()):
            # print("At tag: ", x, x.string, x.attrs, x.findChildren(recursive=False))
            if not x.string and not x.attrs and len(x.findChildren(recursive=False)) <= 1:
                # print("Unwrapping!")
                x.unwrap()

    def unwrap_span(self, soup):
        # Unwrap all style tags
        for x in soup.find_all("span"):
            x.unwrap()

        # TODO: Add unittests

        # Replace all redundant newlines and whitespaces with a single newline or whitespace
        for x in soup():

            if x.string:
                bfr = x.string
                x.string = x.string.replace("\n", " ")
                x.string = re.sub(' +', ' ', x.string).strip()
                print("{} x string is: (befor)".format("-->" if bfr != x.string else ""), bfr)
                print("{} x string is: (after)".format("-->" if bfr != x.string else ""), x.string)

                if len(x.string) <= 2:
                    # Also remove all strings that have less than 2 characters
                    # We can consider this as noise
                    x.string = ""

        # If no other attributes are present,
        # then add the attributes here
        for x in reversed(soup()):
            # print("At tag: ", x, x.string, x.attrs, x.findChildren(recursive=False))
            if not x.string and not x.attrs and len(x.findChildren(recursive=False)) <= 1:
                # print("Unwrapping!")
                x.unwrap()

            # Remove all tags that can be merged

        # TODO: Need to fix encoding issues
        # Designer and fabricator of medical devices, including ventilators for use during the COVID-19 crisis. Selected by NASAâs Jet Propulsion Lab (JPL) to manufacture a new ventilator designed specially for COVID-19 response. Also manufactures other devices, implantables and software products. ISO 13485 Certified.
        # Weâve curated a list of mission-critical resources &	 real-time information for manufacturers &	 distributors.

    def rename_normalize_tags(self, soup):
        """
            Rename all tags to some common ones,
            decide on a few tags to keep
            (lists, buttons)
        :param soup:
        :return:
        """
        # Rename all to div for now
        tags = soup.find('body').findChildren(recursive=False)
        for tag in tags:
            if tag.name != "html" and tag.name != "body" and tag.name != "head":
                tag.name = 'div'

    def tag_entities(self, soup):
        """
            Marks entities as found.
            These can be:
            - Apply named entity recognition, and filter for
            - (1) part-names
            - (2) company names
            - (3) locations
            - (4) (times?)
            - (5) links
        :return:
        """
        for tag in soup():
            if tag.string:
                # Find entities in string
                doc = self.nlp(str(tag.string))
                print("Document is: ", str(tag.string))
                for ent in doc.ents:
                    print("Found entities!")
                    print(ent.text, ent.start_char, ent.end_char, ent.label_)

    def process(self, html, base_url):

        print("Starting single server scraping")
        time1 = time.time()

        soup = BeautifulSoup(str(html), 'lxml')
        print("Time 1: ", time.time() - time1)

        # TODO: The items inside <a> s are ignored?
        # <h2 class="profile-card__title"><a href="/branchloc.html?act=S&amp;cert=29&amp;cid=10083421&amp;cov=NA&amp;goto=%2Fprofile%2F10083421%2Feconopak.html&amp;heading=97010359&amp;navsource=gnb&amp;searchpos=1" rel="nofollow">Econo-Pak</a></h2><span class="supplier-badge--mobile-icon supplier-badge supplier-badge--verified" data-placement="bottom" data-toggle="tooltip" title="This supplierâs location, business information, and complete products/services have been validated.">
        # TODO: Divide and conquer by commenting out some of the below functions

        # TODO: There is probably a much more efficient implementation for all the require ops
        self.remove_tags(soup)
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
        self.remove_attributes(soup)

        for item in soup.contents:
            print("Iterating through contents: ", item)
            if isinstance(item, Doctype):
                print("Yes!")
                item.extract()

        print("Time 4: ", time.time() - time1)

        # TODO: Pop nodes that have only a single child and parent, and not content or attributes
        self.improve_links(soup, base_url)

        print("Time 5: ", time.time() - time1)

        # Iteratively remove all tags that have no content (empty tags)

        # Recursively pass the tree, and delete all leaf nodes that are empty
        # in-order-traversal

        # apply NER; and discard all nodes that do not include a NER component
        # Generator should be run in reverse (in-order-traversal)

        # TODO: Only keep NERs

        # self.remove_empty_nodes(soup)  # not quite the right approach to things
        self.unwrap_span(soup)

        print("Time 6: ", time.time() - time1)

        # rename all the tags into the name "div"
        # self.rename_normalize_tags(soup)

        # self.tag_entities(soup)

        # print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nSoup before prettify: \n\n\n\n\n\n\n\n\n\n")
        # print(soup.prettify())

        self.extract_entities(soup)
        print("Time 7: ", time.time() - time1)


        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nSoup after prettify: \n\n\n\n\n\n\n\n\n\n")
        print(soup.prettify())
        print("Time 8: ", time.time() - time1)

        soup = soup.prettify()

        # Apply named entity recognition, and filter for
        # (1) partnames
        # (2) company names
        # (3) locations
        # (4) (times?)
        # (5) links

        # bonus items are (more difficult to extract)
        # (1) (company descriptions)

        return soup
