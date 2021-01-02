"""
    Implements a downloader which retrieves the markup and saves this into the index.

    Maybe check out this website for random proxies:
    - http-request-randomizer 1.3.2
"""
import time
import random

import requests

# Limit content - length?
# Implement proxies with threadpools, not earlier

# TODO: Skip html files that are larger than 300kB (mark as skipped)

class Downloader:

    def set_proxy(self):


    def __init__(self, proxy_list):
        # Prepare proxies list:
        self.proxy_list = proxy_list
        self.set_proxy()


    def get(self, url):
        """
            retrieve the website markup
        """

        # assert false if the input is not of type HTML! might be malicious otherwise

        # print("Sleep... Proxy is: ", proxy)
        time.sleep(self.sleeptime)
        time.sleep(random.random() * self.sleeptime)

        # Try again if the proxy is just a bad one
        # Check if the proxy list is errorous
        response = requests.get(
            url,
            headers=self.headers,
            proxies={"http": self.proxy, "https": self.proxy},
            timeout=20.
        )
        # print("Response is: ", response)
        content = response.text
        # print("content is: ", content)

        # TODO: if proxy created an error, kick it out from the dictionary

        # Do some basic sanitizing
        # content = bleach.clean(content)
        # let's assume no one on the web is trying to fuck you lol

        # This cleaner is too strong!
        # content = clean_html(content)

        # TODO: This removes the html head!!!
        # Perhaps do now clean but just put this into the database
        # links, meta, page_structure,

        response_code = response.status_code

        return content, response_code

    # TODO: Create a separate object / spiders that can process
    # the webpages and generate / populate the queue
    # the processing of links should probably best be separate


if __name__ == "__main__":
    print("Starting indexer")

    # Testing a single download

