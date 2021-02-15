import datetime as dt
from urllib.parse import urlencode


import scrapy
from scrapy import Selector

import invest_crawler.consts as CONST
from invest_crawler.items.apt_trade import AptTradeScrapy

import pandas as pd

class TradeSpider(scrapy.spiders.XMLFeedSpider):
    name = 'trade'

    def start_requests(self):
        page_num = 1
        date = dt.datetime(2006, 1, 1)
        urls = [
            CONST.APT_DETAIL_ENDPOINT
        ]
        params = {
            "pageNo":str(page_num),
            "numOfRows":"999",
            "LAWD_CD":"44133",
            "DEAL_YMD":date.strftime("%Y%m"),
        }
        for url in urls:
            url += urlencode(params)
            print(url)
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(page_num=page_num, date=date))


    def parse(self, response, page_num, date):
        selector=Selector(response, type='xml')
        items=selector.xpath('//%s'%self.itertag)
        
        apt_trades = [self.parse_item(item) for item in items]
        apt_dataframe = pd.DataFrame.from_records([apt_trade.to_dict() for apt_trade in apt_trades])

        writer = pd.ExcelWriter('APT_TRADE.xlsx', engine='xlsxwriter')
        apt_dataframe.to_excel(writer, sheet_name='Cheonan', index=False)
        writer.save()

        '''
        for item in items:
            apt_trade=self.parse_item(item)
            print(apt_trade)
        '''

    def parse_item(self, item):
        state = "천안시"
        district = "서북구"

        try:
            apt_trade_data = AptTradeScrapy(
                apt_name=item.xpath("./아파트/text()").get().strip(),
                address_1=state,
                address_2=district,
                address_3=item.xpath("./법정동/text()").get().strip(),
                address_4=item.xpath("./지번/text()").get().strip(),
                address=state + " " + district + " " + item.xpath("./법정동/text()").get().strip() + " " +
                    item.xpath("./지번/text()").get().strip(),
                age=item.xpath("./건축년도/text()").get().strip(),
                level=item.xpath("./층/text()").get(),
                available_space=item.xpath("./전용면적/text()").get(),
                trade_date=item.xpath("./년/text()").get() + "/" +
                           item.xpath("./월/text()").get() + "/" +
                           item.xpath("./일/text()").get(),
                trade_amount=item.xpath("./거래금액/text()").get().strip().replace(',', ''),
            )
        except Exception as e:
            print(e)
            self.logger.error(item)
            self.logger.error(item.xpath("./아파트/text()").get())

        return apt_trade_data
