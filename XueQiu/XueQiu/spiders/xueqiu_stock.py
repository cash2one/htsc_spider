# -*- coding: utf-8 -*-

import json
import logging
import time

import html2text
import scrapy
from scrapy.exceptions import CloseSpider

from common.config import RedisKeys
from common.items import NewsItem
from common.utils import TimeUtils
from scrapy_redis.connection import get_redis_conn
from Cython.Shadow import NULL

class XueQiuStockSpider(scrapy.Spider):
    name = "xueqiustock_spider"

    logger = logging.getLogger("htsc")
    start_urls = ["https://xueqiu.com/hq"]
    endDate=None
    
    headers = {"Connection":"keep-alive", \
               "Accept-Encoding":"gzip, deflate, sdch, br", \
               "Accept-Language":"zh-CN,zh;q=0.8,en;q=0.6,en-US;q=0.4", \
               "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36", \
               "Referer":"https://xueqiu.com/today/all?page=1", \
               "Accept":"application/json, text/javascript, */*; q=0.01", \
               "Host":" xueqiu.com", \
               "pragma": "no-cache", \
               "X-Requested-With": "XMLHttpRequest", \
               #"cookie":"xq_a_token=865ed4667a1e51e1f7c09925ff003c190b2af01b", \
               "cache-control": "no-cache"
              }
    def __init__(self, *a, **kw):
        if kw.has_key("endDate"):
            if TimeUtils.isValidEndDate(kw["endDate"]):
                self.endDate=kw["endDate"]
            else:
                self.logger.error(kw["endDate"]+': error format, must be like 2016-05-15')
                raise CloseSpider(kw["endDate"]+' error format')
            
        self.redis_conn=get_redis_conn()

    def parse(self, response):
        access_token_list = response.xpath('//script').re('SNB.data.access_token.*\|\| "(.*)";')
        if len(access_token_list) == 0:
            self.logger.error("get access_token error")
            return
        
        self.headers["cookie"]="xq_a_token="+access_token_list[0]
        
        print access_token_list[0]
        
        #stockName=response.xpath('//div[@class="topName"]/*/strong/text()').extract()[0]

        #name=stockName[0:stockName.rindex("(")]
         
        time_stamp=str(time.time())[0:-3]
        topic_cn_url="https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SH600075&hl=0&source=all&page=1&sort=time&_="+time_stamp
        topic_cn_request = scrapy.Request(topic_cn_url,headers=self.headers,callback=self.parse_list)
        topic_cn_request.meta['scope']=u"个股"
        #topic_cn_request.meta['stock_name']=name
        
        yield topic_cn_request
        
        
    def parse_list(self, response):
        
        nextPage=True
        result = json.loads(response.body_as_unicode())
        scope=response.meta['scope']
        #stock_name=response.meta['stock_name']        
        for i in range(10):
            target=result["list"][i]["target"]
            if target == "_blank":
                continue
            
            item = NewsItem()
            
            item["title"] =result["list"][i]["title"]
            item["content"] =result["list"][i]["text"]
            
            timeStamp=int(result["list"][i]["created_at"])/1000
            print timeStamp
            timeArray =time.localtime(timeStamp)
            pub_date= time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            print "pub_date:"+pub_date
            item['pub_date']=pub_date
            print self.endDate
            if self.endDate is None:
                
                self.endDate=time.strftime("%Y-%m-%d", time.localtime())
            print self.endDate
            if pub_date < self.endDate:
                nextPage=False
            
            item["source"]=result["list"][i]["source"]
             
            #item["name"] =stock_name
            item["scope"] =scope
            item["code"] =result["symbol"][2:]
        
            url="https://xueqiu.com/"+target
            item["url"] = url
            if nextPage is True:
                page=int(result["page"])+1
                time_stamp=str(time.time())[0:-3]
                
                url="https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=SH600075&hl=0&source=all&sort=time&_="+time_stamp+"&page="+str(page)
                request = scrapy.Request(url,headers=self.headers,callback=self.parse_list)
                yield request
            
            yield item
            