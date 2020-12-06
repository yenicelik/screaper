"""
    Implements a downloader which retrieves the markup and saves this into the index
"""
import time
import json
import random

import requests
from urllib.request import urlopen
from lxml.html.clean import clean_html

from screaper.resources.db import resource_database

# Limit content - length?
# Implement proxies with threadpools, not earlier

class Downloader:

    def load_proxy_list(self):

        json_url = "https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json"
        with urlopen(json_url) as url:
            proxies = json.loads(url.read().decode('utf-8'))

        proxies = proxies['proxies']
        print("Proxies are: ", proxies)

        # TODO: Replace with environment variable
        proxies = [(x["ip"], x["port"]) for x in proxies if x["google_status"] == 200]
        proxies = [("http://" + str(x[0]) + ":" + str(x[1])) for x in proxies]

        return proxies


    def __init__(self):
        # Prepare proxies list:
        self.proxies = self.load_proxy_list()

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",  # (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)
            "From": "contact@theaicompany.com"
        }
        self.sleeptime = 0.5

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

        # proxy = random.choice(self.proxies)
        # print("Sleep... Proxy is: ", proxy)
        time.sleep(self.sleeptime)
        time.sleep(random.random() * 0.5)

        response = requests.get(
            url,
            headers=self.headers,
            # proxies={"http": proxy, "https": proxy},
            # timeout=2.
        )
        # print("Response is: ", response)
        content = response.text
        # print("content is: ", content)

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
