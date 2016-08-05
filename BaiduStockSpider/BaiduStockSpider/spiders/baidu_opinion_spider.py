# -*- coding: utf-8 -*-

import json
import logging
import re
import time

import scrapy
from scrapy.exceptions import CloseSpider

from common.config import RedisKeys
from common.items import BaiduStockOpinionItem
from common.utils import TimeUtils
from scrapy_redis.connection import get_redis_conn 


class BaiduStockSpider(scrapy.Spider):
    logger = logging.getLogger("htsc")
    
    name = "baidu_opinion_spider"
    endDate=None
    nextPage=True  #whether to get next page
    redis_conn=None
    current_date=str(time.strftime("%Y%m%d", time.localtime())) #20160521
    batch=1
    start_urls = ["http://client.gushitong.baidu.com/concept/getopinion?from=android&os_ver=21&format=json&vv=3.3.0&uid=&BDUSS=&cuid=7669213303303402648D8EE6C551460D|843699320590268&channel=1011320a&device=MX4&logid=1461677511&actionid=1461677502&device_net_type=wifi&type=0&page=0",
                  "http://client.gushitong.baidu.com/concept/getopinion?from=android&os_ver=21&format=json&vv=3.3.0&uid=&BDUSS=&cuid=7669213303303402648D8EE6C551460D|843699320590268&channel=1011320a&device=MX4&logid=1461677511&actionid=1461677502&device_net_type=wifi&type=1&page=0"
    ]
    
    def __init__(self, *a, **kw):
        if kw.has_key("endDate"):
            if TimeUtils.isValidEndDate(kw["endDate"]):
                self.endDate=kw["endDate"].replace("-","")
            else:
                self.logger.error(kw["endDate"]+': error format, must be like 2016-05-15')
                raise CloseSpider(kw["endDate"]+' error format')
            
        if kw.has_key("batch"):
            self.batch=kw['batch']
            
        self.redis_conn=get_redis_conn()
            
        
    def parse(self, response):
        result = re.findall(r'type=(\d+)',response.url)
        flag=result[0]
                
        jsonresponse = json.loads(response.body_as_unicode())
        try:
            if self.endDate is None:
                historyOpinion=jsonresponse["data"]["historyOpinion"][0]  #only get current day
                latest_date=historyOpinion['opinionTime']
                self.logger.debug("latest_date: "+latest_date)
                self.logger.debug("current_date: "+self.current_date)
                latest_date=latest_date.encode('UTF-8','ignore')
                if latest_date != self.current_date:
                    current_time=str(time.strftime("%Y%m%d  %H:%M:%S", time.localtime()))
                    self.logger.debug("there is no data in current time: "+current_time)
                    return
                
                self.logger.debug("start to crawl date: "+latest_date)
                stocks=historyOpinion['hotSearchOpinionDetail']
                for i in range(5):
                    item=BaiduStockOpinionItem()
                    item['pub_date']=latest_date
                    item['batch']=int(self.batch)
                    item['code']=stocks[i]['stockCode']
                    item['name']=stocks[i]['stockName']
                    rankString=stocks[i]['showtext']  # No.1
                    item['rank']=int(rankString.split('.')[1])
                    opinionKeywords=stocks[i]['opinionKeywords']
                    item['keywords']=",".join(opinionKeywords)
                    item['flag']=int(flag)
                    item['crawl_ts']=TimeUtils.getCurrentTimeStamp()
                    yield item
            else:
                for historyOpinion in jsonresponse["data"]["historyOpinion"]:
                    latest_date=historyOpinion['opinionTime']
                    #print "test in redis"
                    if self.endDate <= latest_date and self.redis_conn.zscore(RedisKeys.baidu_opinion_crawled+flag, \
                        latest_date) is None:  #redis 是否已爬取
                        #print "crawl Date: "+latest_date
                        self.logger.info("start to crawl date: "+latest_date)
                        stocks=historyOpinion['hotSearchOpinionDetail']
                        for i in range(5):
                            item=BaiduStockOpinionItem()
                            item['pub_date']=latest_date
                            item['batch']=int(self.batch)
                            item['code']=stocks[i]['stockCode']
                            item['name']=stocks[i]['stockName']
                            rankString=stocks[i]['showtext']  # No.1
                            item['rank']=int(rankString.split('.')[1])
                            opinionKeywords=stocks[i]['opinionKeywords']
                            item['keywords']=",".join(opinionKeywords)
                            item['flag']=int(flag)
                            item['crawl_ts']=TimeUtils.getCurrentTimeStamp()
                            yield item
                    elif self.endDate <= latest_date and self.redis_conn.zscore(RedisKeys.baidu_opinion_crawled+flag, \
                        latest_date) is not None:
                        continue
                    else:
                        self.nextPage=False
                        break
                
                if self.nextPage:
                    page = int(response.url[-1])+1
                    url = response.url[0:-1] + str(page)
                    request = scrapy.Request(url, callback=self.parse)
                    yield request
        except KeyError as e:
            self.logger.error("exception is %s" % e)
