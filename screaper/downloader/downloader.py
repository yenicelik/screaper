"""
    Implements a downloader which retrieves the markup and saves this into the index
"""
import time

import requests
from lxml.html.clean import clean_html

from screaper.resources.db import resource_database


class Downloader:

    def __init__(self):
        self.headers = headers = {
            "User-Agent": "Mozilla/5.0",  # (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)
            "From": "contact@theaicompany.com"
        }
        self.sleeptime = 2.0

    def add_to_index(self, url, markup):
        """
            Adds a downloaded item to the markup
        """

        # For now, analyse any kind of markup
        resource_database.create_markup_record(
            url=url,
            markup=markup,
            skip=False
        )
        resource_database.commit()

    def get(self, url):
        """
            retrieve the website markup
        """

        print("Sleep...")
        time.sleep(self.sleeptime)

        response = requests.get(url, headers=self.headers)
        print("Response is: ", response)
        content = response.text
        print("content is: ", content)

        # Do some basic sanitizing
        # content = bleach.clean(content)
        # let's assume no one on the web is trying to fuck you lol
        content = clean_html(content)
        response_code = response.status_code

        return content, response_code

    # TODO: Create a separate object / spiders that can process
    # the webpages and generate / populate the queue
    # the processing of links should probably best be separate


downloader = Downloader()



if __name__ == "__main__":
    print("Starting indexer")
