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


class XueQiuSpider(scrapy.Spider):
    name = "xueqiu_spider"

    logger = logging.getLogger("htsc")
    start_urls = ["https://xueqiu.com/hq"]
    #allowed_domains = ['xueqiu.com']

    pageControl={} #whether to crawl next page  Next,Stop
    endDate=None
    redis_conn=None
    
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
    
    
    '''
    def start_requests(self):
        request = scrapy.Request("https://xueqiu.com/hq", callback=self.parse_token)
        yield request
    ''' 
        
    def parse(self, response):
        access_token_list = response.xpath('//script').re('SNB.data.access_token.*\|\| "(.*)";')
        if len(access_token_list) == 0:
            self.logger.error("get access_token error")
            return
        
        self.headers["cookie"]="xq_a_token="+access_token_list[0]
        time_stamp=str(time.time())[0:-3]
        topic_cn_url="https://xueqiu.com/statuses/topic.json?simple_user=1&filter_text=1&topicType=5&_="+time_stamp+"&page=1"
        topic_cn_request = scrapy.Request(topic_cn_url,headers=self.headers, callback=self.parse_list)
        topic_cn_request.meta['scope']=u"沪深"
        yield topic_cn_request
        
        topic_us_url="https://xueqiu.com/statuses/topic.json?simple_user=1&filter_text=1&topicType=1&_="+time_stamp+"&page=1"
        topic_us_request = scrapy.Request(topic_us_url,headers=self.headers,callback=self.parse_list)
        topic_us_request.meta['scope']=u"美股"
        yield topic_us_request
        
        topic_hk_url="https://xueqiu.com/statuses/topic.json?simple_user=1&filter_text=1&topicType=2&_="+time_stamp+"&page=1"
        topic_hk_request = scrapy.Request(topic_hk_url,headers=self.headers,callback=self.parse_list)
        topic_hk_request.meta['scope']=u"港股"
        yield topic_hk_request
        
        topic_lc_url="https://xueqiu.com/statuses/topic.json?simple_user=1&filter_text=1&topicType=4&_="+time_stamp+"&page=1"
        topic_lc_request = scrapy.Request(topic_lc_url,headers=self.headers,callback=self.parse_list)
        topic_lc_request.meta['scope']=u"理财"
        yield topic_lc_request
        
    
    def parse_list(self, response):
        result = json.loads(response.body_as_unicode())
        scope=response.meta['scope']
        nextPage=True
        less_than_endDate_time=int(0)
        for i in range(20):
            target=result[i]["target"]
            if target == "_blank":
                continue
            
            item = NewsItem()
            url="https://xueqiu.com/"+target
            item["url"] = url
            if self.redis_conn.zscore(RedisKeys.xueqiu_url_crawled, url) is not None:
                self.logger.debug('url has benn got: '+url)
                continue
            
            item["scope"]=scope
            item["title"]=result[i]["topic_title"]
            print "title: "+item["title"]
            pub_date = result[i]['timeBefore']   #str
            print "pub_date: "+pub_date
            if pub_date.find(u"今天") != -1: #今天 17:24
                pub_date=TimeUtils.getCurrentDate()+pub_date[2:]+":00"
            elif pub_date.find(u"分钟前") !=-1:
                minute_before=pub_date[0:pub_date.find(u"分钟前")]
                pub_date=TimeUtils.getDateSubtractMinutes(int(minute_before))
            else: #07-13 14:08
                pub_date=TimeUtils.getCurrentYear()+"-"+pub_date+":00"
            print "pub_date: "+pub_date
            item["pub_date"]=pub_date
            if pub_date < self.endDate:
                less_than_endDate_time += 1
            
            article_id=str(result[i]["id"])
            user_id=str(result[i]["user_id"])
            item["id"]=user_id+"&&"+article_id+"&&"
            request = scrapy.Request(url,headers=self.headers,callback=self.parse_article)
            request.meta['item'] = item
            request.meta['user_id'] = user_id
            request.meta['id'] = article_id
            yield request
        
        if less_than_endDate_time > 4: #at least 4 times, 避免老数据以为修改显示在前面
            nextPage=False
            
        if nextPage is True:
            page=int(response.url[-1])+1
            time_stamp=str(time.time())[0:-3]
            url="https://xueqiu.com/statuses/topic.json?simple_user=1&filter_text=1&topicType=0&_="+time_stamp+"&page="+str(page)
            request = scrapy.Request(url,headers=self.headers,callback=self.parse_list)
            yield request
        

    def parse_article(self, response):
        item=response.meta["item"]
        item["crawl_ts"]=TimeUtils.getCurrentTimeStamp()
        #某些文章内容中没有title
        #title = response.xpath("//div[@class='status-content']/h4[@class='status-title']/text()").extract()[0]
        #print "title: "+title
        
        #retrieve content
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        raw = response.xpath("//div[@class='status-content']/div[@class='detail']/text()").extract()[0]
        content = converter.handle(raw)
        item["content"] = content
        print "content: "+content

        # retrieve source
        src_raw = response.xpath("//div[@class='subtitle']/span[@class='source']/text()").extract()[0]
        src_txt = converter.handle(src_raw).strip()
        source = src_txt[2:]
        item["article_source"]=source
        print "article_source: "+source
        
        yield item
        
