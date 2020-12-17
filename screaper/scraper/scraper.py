"""
    Implements a scraper which processes the downloaded markup.

    Some good scraping resources:
    - https://python.hotexamples.com/examples/BeautifulSoup/BeautifulSoup/recursiveChildGenerator/python-beautifulsoup-recursivechildgenerator-method-examples.html

"""
import re

from bs4 import BeautifulSoup, Comment, Doctype, NavigableString

# fout.write(re.sub('\s+', ' ', line))

# TODO: Return triplets that describe a sparse graph ?

class Scraper:

    # def _replace_by_paragraph(soup, tag):
    #     for t in soup.findAll(tag):
    #         t.name = "p"
    #         t.attrs = {}

    def __init__(self):
        self.remove_attributes = set([
            'lang', 'language', 'onmouseover', 'onmouseout', 'script', 'style',
            'font', 'dir', 'face', 'size', 'color', 'style', 'class', 'width',
            'height', 'hspace', 'border', 'valign', 'align', 'background', 'bgcolor',
            'text', 'link', 'vlink', 'alink', 'cellpadding', 'cellspacing', 'data-cert_id',
            'type'
            # added newly
            'src', 'target'
        ])

        # Extent whitelist with any additional items that may be useful for future usage!!!
        self.attribute_whitelist = set([
            "href", "value", "title", "summary", "data-content",
            "cols", "colspan", "rows", "rowspan", "content",
            "data", "datetime", "label", "list", "srcdoc", 'description',
            "name"
        ])

    def remove_tag(self, soup, tag_name):
        for x in soup.find_all(tag_name):
            x.decompose()

    def remove_tags(self, soup):
        tags = [
            "scripts", "style", "noscript", "footer",
            "svg", "link", "input", "form", "button",
            "br", "class",
            # slightly optional
            "select",

        ]
        for x in soup.find_all(tags):
            x.decompose()

        # self.remove_tag(soup, isinstance(text, Comment))
        # can probably also remove input tags
        # can probably also remove form tags

    def remove_attributes(self, soup):
        pass

    def process(self, html, base_url):
        soup = BeautifulSoup(str(html), 'lxml')

        # TODO: There is probably a much more efficient implementation for all the require ops
        self.remove_tags(soup)

        # img can include href tags.
        # if img does not includes href tag, remove this

        # slightly optional
        for element in soup(text=lambda it: isinstance(it, Comment)):
            element.extract()

        for x in soup.find_all(attrs={"name": "google-site-verification"}):
            x.decompose()

        # Apply whitelist of attributes
        # Check if whitelist misses anything super-important!
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
                    if attr in self.remove_attributes:
                        print("Popping: ", attr)
                        del_attr.add(attr)
                for x in del_attr:
                    s.attrs.pop(x)

        for item in soup.contents:
            print("Iterating through contents: ", item)
            if isinstance(item, Doctype):
                print("Yes!")
                item.extract()

        for link in soup.find_all('a'):

            if 'href' not in link.attrs:
                # What to do in this case?
                continue

            url = link.attrs['href'].strip()

            if url is None:
                # TODO: Log a warning that some url is none!
                continue
            # apply whitelisting
            if url == "":
                # if link is empty, it is probably broken, skip
                continue
            if url[0] == "#":
                # if link starts with "#", skip this (because this is just an anchor
                continue
            if url[0] == "/":
                # if link starts with slash, then this is a relative link. We append the domain to the url
                link.attrs['href'] = base_url + url

            # print("Link is: ", link.attrs['href'])

        # TODO: Pop nodes that have only a single child and parent, and not content or attributes


        # Iteratively remove all tags that have no content (empty tags)

        # Recursively pass the tree, and delete all leaf nodes that are empty
        # in-order-traversal

        # apply NER; and discard all nodes that do not include a NER component
        # Generator should be run in reverse (in-order-traversal)
        remove_redundant = True
        # if remove_redundant:
        #     for node in soup.recursiveChildGenerator():
        #         print("Node is: ", node)
        #
        #         if isinstance(node, NavigableString):
        #
        #             if not node.strip():
        #                 # Remove this from the parse tree if this is an empty text
        #                 node.extract()
        #
        #             continue
        #
        #         # Get all children of the node
        #         if len(node.find_all()) == 0:
        #             print("No children found, can delete this node unwrap: ", node)
        #
        #             if not node.get_text():
        #                 print("No text found (1) , can unwrap: ", node)
        #                 node.decompose()
        #             if node.get_text() and node.get_text().strip() == "":
        #                 print("No text found (2), can unwrap: ", node)
        #                 node.decompose()
        #
        #         elif len(node.find_all()) == 1:
        #             print("Only one child found. Can safely unwrap this tag")
        #             if not node.get_text():
        #                 node.unwrap()
        #             if node.get_text() and node.get_text().strip() == "":
        #                 node.unwrap()
        #
        #         else:
        #             print("Node cannot be safely deleted")

        remove_redundant = True
        if remove_redundant:
            # Iterate each line
            for x in soup.find_all():

                # fetching text from tag and remove whitespaces
                # Empty attributes!
                print("x is: ", x.get_text().replace("\n", " ").strip())
                print("x is: ", len(x.get_text().replace("\n", " ").strip()))

                # Also check if there's any children (unless we do in-order node traversal
                # Actually, this should be correct, bcs get text gets the text collectively

                # TODO: But then we must check if any child nodes have any attributes!!
                # We can

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

        print("Soup before prettify: ")
        print(soup)

        soup = soup.prettify()

        # if not s.contents or s.contents.strip() in [" ", ""]:
        #     print("Tag is empty!", s)
        #     s.unwrap()


        print("\n\n\n\n\n\n\n\n\n\n\n\nEXTRACTED\n\n\n\n\n\n\n\n\n\n\n\n")


        # Finally, unwrap until nothing is there to unwrap anymore
        # soup = soup.unwrap


        # Remove all links that have href="#" (broken link, or javascript link, so useless...)

        # turn all links into global links
        # base_url

        # map(lambda x: x.decompose(), soup.findAll("embed"))

        # TODO: Replace all links by global links

        # map(lambda x: x.decompose(), soup.findAll("navbar"))  # includes proximity informtaion, so keep this
        # map(lambda x: x.decompose(), soup.findAll("nav"))  # includes proximity informtaion, so keep this

        print("Soup after extract")
        print(soup)

        # text = soup.get_text()
        # text = "\n".join(line.strip() for line in text.split("\n") if line.strip() != "")

        # return text
