import scrapy
from scrapy import Request, signals
from scrapy.exceptions import DontCloseSpider


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    # def start_requests(self):
    #     urls = [
    #         'http://quotes.toscrape.com/page/1/',
    #         'http://quotes.toscrape.com/page/2/',
    #     ]
    #     for url in urls:
    #         yield scrapy.Request(url=url, callback=self.parse)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        spider.crawler.signals.connect(spider.spider_idle, signal=signals.spider_idle)
        return spider

    def spider_idle(self):
        self.log("Spider idle signal caught.")
        raise DontCloseSpider

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'quotes-{page}.html'
        self.log(f'Saved file {filename}')

        urls = response.xpath('//a/@href').extract()
        for url in urls:
            if not (url.startswith('http://') or url.startswith('https://')):
                continue
            print("Adding to crawl frontier: ", url)
            yield Request(url, callback=self.parse)
