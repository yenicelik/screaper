"""
    Implements a scraper which processes the downloaded markup
"""
from bs4 import BeautifulSoup


class Scraper:

    def _replace_by_paragraph(soup, tag):
        for t in soup.findAll(tag):
            t.name = "p"
            t.attrs = {}

    def __init__(self):
        pass

    def process(self, html):
        soup = BeautifulSoup(str(html))

        map(lambda x: x.extract(), soup.findAll("code"))
        map(lambda x: x.extract(), soup.findAll("script"))
        map(lambda x: x.extract(), soup.findAll("pre"))
        map(lambda x: x.extract(), soup.findAll("style"))
        map(lambda x: x.extract(), soup.findAll("embed"))
