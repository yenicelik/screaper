"""
    Implements a markup processor
"""
from pyquery import PyQuery as pq
from url_parser import get_base_url


class MarkupProcessor:

    def __init__(self):
        pass

    def get_links(self, url, markup):

        out = []

        pyquery_object = pq(markup)
        for link in pyquery_object('a').items():

            # print("Link looks as follows: ", link, type(link))
            link = link.attr['href']  # only grab the href attribute

            if link is None:
                # if link is None, then just skip (for whatever reasons of the website, or the crawler
                continue
            if link.strip() == "":
                # if link is empty, it is probably broken, skip
                continue
            if link.strip()[0] == "#":
                # if link starts with "#", skip this (because this is just an anchor
                continue
            if link.strip()[0] == "/":
                # if link starts with slash, then this is a relative link. We append the domain to the url
                basic_url = get_base_url(url)  # Returns just the main url
                link = basic_url + link

            # Other ways to check if link is valid?
            # TODO: Implement contents to also be exported

            out.append(link)
            # print(link)

        return out

markup_processor = MarkupProcessor()
            
if __name__ == "__main__":
    print("Markup processor is: ")
