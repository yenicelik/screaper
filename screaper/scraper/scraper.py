"""
    Implements a scraper which processes the downloaded markup
"""
from bs4 import BeautifulSoup


class Scraper:

    # def _replace_by_paragraph(soup, tag):
    #     for t in soup.findAll(tag):
    #         t.name = "p"
    #         t.attrs = {}

    def __init__(self):
        pass

    def process(self, html):
        soup = BeautifulSoup(str(html), 'lxml')

        map(lambda x: x.extract(), soup.findAll("code"))
        map(lambda x: x.extract(), soup.findAll("script"))
        map(lambda x: x.extract(), soup.findAll("pre"))
        map(lambda x: x.extract(), soup.findAll("style"))
        map(lambda x: x.extract(), soup.findAll("embed"))
        map(lambda x: x.extract(), soup.findAll("svg"))
        map(lambda x: x.extract(), soup.findAll("noscript"))
        # map(lambda x: x.extract(), soup.findAll("footer"))
        # map(lambda x: x.extract(), soup.findAll("navbar"))
        # map(lambda x: x.extract(), soup.findAll("nav"))

        # map(lambda x: x.extract(), soup.findAll(attribute=True))

        print("Soup before extract")
        print(soup)
        print("\n\n\nEXTRACTED")

        text = soup.get_text()
        text = "\n".join(line.strip() for line in text.split("\n") if line.strip() != "")

        # Remove all stopwords. Or actually, let's not do this for now (bcs scalability and no strict need)

        # TODO: Automatically detect urls in text


        print("Soup is: ")
        print(text)

        # print("html string is: ", html)

        # Too restrictive, I believe
        # extracted = trafilatura.extract(html, include_comments=False)
        # print("Extracted items are: ")
        # print(extracted)

        return text
