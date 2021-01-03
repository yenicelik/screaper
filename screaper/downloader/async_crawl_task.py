import asyncio
import random

from aiohttp import ClientHttpProxyError
from aiohttp_requests import requests
from requests.exceptions import ProxyError, ConnectTimeout

from screaper.engine.markup_processor import markup_processor


class CrawlAsyncTask:
    """
        Implements a single Crawl Operation.
        Similar to a thread, but modeled as an async task
    """

    def __init__(self, proxy_list, queue_obj):
        self.proxy_list = proxy_list
        self.queue_obj = queue_obj

        # Remove the sleeptime. Or no, actually, keep it
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
        # (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)
        }
        self.sleeptime = 0.35  # 0.35

    async def fetch(self):
        proxy = random.choice(self.proxy_list.proxies)
        # proxy = None

        print("Proxy is now: ", proxy)

        # Make the asyncronous request

        # Fetch the request

        # Add the markup to the database
        # Ping the contents of the website
        await asyncio.sleep(self.sleeptime)
        await asyncio.sleep(random.random() * self.sleeptime)

        try:

            # Make the asyncio request
            response = await requests.get(
                self.queue_obj.url,
                headers=self.headers,
                proxy=proxy,
                timeout=20.
            )
            markup = await response.text()
            status_code = response.status
            target_urls = markup_processor.get_links(self.queue_obj.url, markup)

        except ProxyError as e:
            print("Connection Timeout Exception 1!", e)
            self.proxy_list.warn_proxy(proxy)
            return None, e, []

        except ConnectTimeout as e:
            print("Connection Timeout Exception 2!", e)
            self.proxy_list.warn_proxy(proxy)
            return None, e, []

        except ClientHttpProxyError as e:
            print("Connection Timeout Exception 3!", e)
            self.proxy_list.warn_proxy(proxy, harsh=True)
            return None, e, []

        except Exception as e:
            print("Encountered exception: ", e)
            return None, e, []

        return status_code, markup, target_urls

if __name__ == "__main__":
    print("Making an example request with the async crawl task")

    from screaper_resources.resources.resouces_proxylist import ProxyList
    from screaper.crawl_frontier.crawl_frontier import CrawlFrontier
    from screaper_resources.resources.db import Database

    proxy_list = ProxyList()
    database = Database()
    queue_obj = CrawlFrontier(database).pop_start()

    print("Queue obj is: ", queue_obj)

    single_execution = CrawlAsyncTask(proxy_list, queue_obj=queue_obj)
    print(asyncio.run(single_execution.fetch()))