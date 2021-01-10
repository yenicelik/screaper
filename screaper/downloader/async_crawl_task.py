import asyncio
import random

from aiohttp import ClientHttpProxyError
from aiohttp_requests import requests
from flashtext import KeywordProcessor
from requests.exceptions import ProxyError, ConnectTimeout

from screaper.engine.markup_processor import markup_processor


# TODO: Implement Caching requests.
# DNS Cache
# Headers Cache
# Cookies Cache

class CrawlAsyncTask:
    """
        Implements a single Crawl Operation.
        Similar to a thread, but modeled as an async task
    """

    def __init__(self, proxy_list, crawl_object):
        self.proxy_list = proxy_list
        self.crawl_object = crawl_object

        self.url = crawl_object.url
        self.depth = crawl_object.depth

        # Select at random some header
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            # (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)
        }
        self.sleeptime = 0.35  # 0.35

        self.keyword_processor = KeywordProcessor()
        self.keyword_processor.add_keywords_from_list(['bearing'])

        self.link_processor = LinkProcessor()

    def score(self, markup):
        return len(self.keyword_processor.extract_keywords(markup))

    async def fetch(self):
        proxy = random.choice(self.proxy_list.proxies)

        # Add the markup to the database
        # Ping the contents of the website
        await asyncio.sleep(self.sleeptime)
        await asyncio.sleep(random.random() * self.sleeptime)

        try:

            # Make the async request
            response = await requests.get(
                self.url,
                headers=self.headers,
                proxy=proxy,
                timeout=15.0
            )
            self.crawl_object.markup = await response.text()
            self.crawl_object.status_code = response.status
            self.crawl_object.target_urls = markup_processor.get_links(self.url, self.crawl_object.markup)

        except ProxyError as e:
            # print("Connection Timeout Exception 1!", e)
            self.proxy_list.warn_proxy(proxy)
            self.crawl_object.add_error(e)

        except ConnectTimeout as e:
            # print("Connection Timeout Exception 2!", e)
            self.proxy_list.warn_proxy(proxy)
            self.crawl_object.add_error(e)

        except ClientHttpProxyError as e:
            # print("Connection Timeout Exception 3!", e)
            self.proxy_list.warn_proxy(proxy, harsh=True)
            self.crawl_object.add_error(e)

        except Exception as e:
            print("Encountered exception: ", e)
            self.crawl_object.add_error(e)

        if not (self.crawl_object.status_code == requests.codes.ok):
            self.crawl_object.add_error(self.crawl_object.markup)

        # Calculate the score otherwise by measuring how many tokens in the markup match with the dictionary
        self.crawl_object.score = self.score(self.crawl_object.markup)

        # Process all the links
        self.crawl_object.target_urls = list(set([self.link_processor.process(x, self.crawl_object.url) for x in self.crawl_object.target_urls]))

        return self.crawl_object


if __name__ == "__main__":
    print("Making an example request with the async crawl task")

    from screaper_resources.resources.resouces_proxylist import ProxyList
    from screaper.crawl_frontier.crawl_frontier import CrawlFrontier, LinkProcessor
    from screaper_resources.resources.db import Database

    proxy_list = ProxyList()
    database = Database()
    queue_obj = CrawlFrontier(database).pop_start_list()[0]

    print("Queue obj is: ", queue_obj)

    single_execution = CrawlAsyncTask(proxy_list, url=queue_obj.url)
    print(asyncio.run(single_execution.fetch()))
