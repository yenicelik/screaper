"""
    Implements a downloader which retrieves the markup and saves this into the index.

    Maybe check out this website for random proxies:
    - http-request-randomizer 1.3.2
"""
import time
import json
import random

import requests
from urllib.request import urlopen

# Limit content - length?
# Implement proxies with threadpools, not earlier

# TODO: Skip html files that are larger than 300kB (mark as skipped)

class Downloader:

    def load_proxy_list(self):

        # TODO: Download a fuller list
        json_url = "https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json"
        with urlopen(json_url) as url:
            proxies = json.loads(url.read().decode('utf-8'))

        # TODO: Pop from list once the proxy proves itself to be bad

        proxies = proxies['proxies']

        # TODO: Replace with environment variable
        proxies = [(x["ip"], x["port"]) for x in proxies if x["google_status"] == 200]
        proxies = [("http://" + str(x[0]) + ":" + str(x[1])) for x in proxies]

        return proxies

    def set_proxy(self):
        self.proxy = random.choice(self.proxies)
        print("Proxy is now: ", self.proxy)

    def __init__(self, resource_database):
        self.resource_database = resource_database
        # Prepare proxies list:
        self.proxies = self.load_proxy_list()  # TODO: Move this variable one level up?
        self.set_proxy()

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",  # (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)
        }
        self.sleeptime = 0.35  # 0.35

    def add_to_index(self, url, markup):
        """
            Adds a downloaded item to the markup
        """

        # For now, analyse any kind of markup
        self.resource_database.create_markup_record(
            url=url,
            markup=markup
        )
        self.resource_database.commit()

    def get(self, url):
        """
            retrieve the website markup
        """

        # assert false if the input is not of type HTML! might be malicious otherwise

        # print("Sleep... Proxy is: ", proxy)
        time.sleep(self.sleeptime)
        time.sleep(random.random() * self.sleeptime)

        # Try again if the proxy is just a bad one
        response = requests.get(
            url,
            headers=self.headers,
            proxies={"http": self.proxy, "https": self.proxy},
            timeout=20.
        )
        # print("Response is: ", response)
        content = response.text
        # print("content is: ", content)

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
