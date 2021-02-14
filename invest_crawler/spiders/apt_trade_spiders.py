import datetime as dt
from urllib.parse import urlencode


import scrapy
from scrapy import Selector

import invest_crawler.consts as CONST


class TradeSpider(scrapy.spiders.XMLFeedSpider):
    name = 'trade'

    def start_requests(self):
        page_num = 1
        date = dt.datetime(2006, 1, 1)
        urls = [
        CONST.APT_DETAIL_ENDPOINT
        ]
        params = {
            "pageNo": str(page_num),
            "numOfRows": "999",
            "LAWD_CD": "44133",
            "DEAL_YMD": date.strftime("%Y%m"),
        }
        for url in urls:
            url += urlencode(params)
            yield scrapy.Request(url=url)


    def parse(self, response):
        print(response.body)