import asyncio
import random
import traceback
from _ssl import SSLCertVerificationError

from aiohttp import ClientHttpProxyError, ClientProxyConnectionError, ServerDisconnectedError, InvalidURL, \
    TooManyRedirects
from aiohttp_requests import requests
from flashtext import KeywordProcessor
from requests.exceptions import ProxyError, ConnectTimeout

from screaper.engine.markup_processor import markup_processor, LinkProcessor


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
        # proxy = None

        # Add the markup to the database
        # Ping the contents of the website
        await asyncio.sleep(self.sleeptime)
        await asyncio.sleep(random.random() * self.sleeptime)
        # print("Fetching :", self.url)

        try:

            # Make the async request
            if proxy is None:
                response = await requests.get(
                    self.url,
                    headers=self.headers,
                    timeout=20.0
                )
            else:
                response = await requests.get(
                    self.url,
                    headers=self.headers,
                    proxy=proxy,
                    timeout=20.0
                )
            self.crawl_object.markup = await response.text()
            self.crawl_object.status_code = response.status
            self.crawl_object.ok = response.ok

        except ProxyError as e:
            # print("Connection Timeout Exception 1!", e)
            self.proxy_list.warn_proxy(proxy)
            self.crawl_object.add_error(e)
            return self.crawl_object

        except ClientHttpProxyError as e:
            # print("Connection Timeout Exception 3!", e)
            self.proxy_list.warn_proxy(proxy)
            self.crawl_object.add_error(e)
            return self.crawl_object

        except ClientProxyConnectionError as e:
            self.proxy_list.warn_proxy(proxy)
            self.crawl_object.add_error(e)
            return self.crawl_object

        except ConnectTimeout as e:
            # print("Connection Timeout Exception 2!", e)
            self.proxy_list.warn_proxy(proxy)
            self.crawl_object.add_error(e)
            return self.crawl_object

        except asyncio.TimeoutError as e:
            self.proxy_list.warn_proxy(proxy)
            self.crawl_object.add_error(e)
            return self.crawl_object

        except ConnectionRefusedError as e:
            self.crawl_object.add_error(e)
            return self.crawl_object

        except ServerDisconnectedError as e:
            self.crawl_object.add_error(e)
            return self.crawl_object

        except InvalidURL as e:
            self.crawl_object.add_error(e)
            return self.crawl_object

        except SSLCertVerificationError as e:
            self.crawl_object.add_error(e)
            return self.crawl_object

        except TooManyRedirects as e:
            self.crawl_object.add_error(e)
            return self.crawl_object

        except Exception as e:
            print("Encountered exception: ", repr(e))
            # traceback.print_exc()
            self.crawl_object.add_error(e)
            print(proxy, self.url)
            return self.crawl_object

        if not (self.crawl_object.ok):
            self.crawl_object.add_error(self.crawl_object.markup)

        if not (self.crawl_object.markup):
            self.crawl_object.add_error((self.crawl_object.status_code, self.crawl_object.markup))

        # Calculate the score otherwise by measuring how many tokens in the markup match with the dictionary
        self.crawl_object.score = self.score(self.crawl_object.markup)

        found_urls = markup_processor.get_links(self.url, self.crawl_object.markup)
        # Process all the links # Propagate the score onwards
        for found_url in found_urls:
            target_url, referrer_url, skip = self.link_processor.process(found_url, self.crawl_object.url)
            self.crawl_object.insert_crawl_next_object(original_crawl_obj=self.crawl_object, target_url=target_url,
                                                       skip=skip, score=self.crawl_object.score)

        return self.crawl_object
