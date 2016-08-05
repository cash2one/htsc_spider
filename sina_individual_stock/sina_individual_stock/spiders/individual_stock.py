# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import re
from time import mktime
import time

import html2text
import scrapy
from scrapy.exceptions import CloseSpider

from common.config import RedisKeys
from common.items import NewsItem
from common.utils import TimeUtils
from scrapy_redis.connection import get_redis_conn


class SinaStockSpider(scrapy.Spider):
    name = "sina_individual_stock_spider"

    logger = logging.getLogger("htsc")
    #allowed_domains = ["sina.com.cn"]
    start_urls = [
#   "http://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php?symbol=sh600000&Page=1",
    ]

    all_stock_urls=[]
    urls_check=[]
    pageControl={} #whether to crawl next page  Next,Stop
    endDate=None
    redis_conn=None

    def __init__(self, *a, **kw):
        if kw.has_key("endDate"):
            if TimeUtils.isValidEndDate(kw["endDate"]):
                self.endDate=kw["endDate"]
            else:
                self.logger.error(kw["endDate"]+': error format, must be like 2016-05-15')
                raise CloseSpider(kw["endDate"]+' error format')
        
        
        self.redis_conn=get_redis_conn()
        #if not self.redis_conn.exists('sina_individual_stock:requests'):
        #    print "set start urls"
        #    self.start_urls = [
        #         "http://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600000.phtml",
        #     "http://vip.stock.finance.sina.com.cn/corp/go.php/vCB_AllNewsStock/symbol/sh600004.phtml"
        #     ]
        sha_stock_codes=self.redis_conn.smembers(RedisKeys.SHAStockCode)
        for code in sha_stock_codes:
            url=('http://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php?symbol=sh%s&Page=1' % code)
            self.start_urls.append(url)

    def parse(self, response):
        m = re.findall(r'\d{6}', response.url)
        stock_code=m[0]
        
        if self.endDate is not None:
            self.pageControl[stock_code] = "Next"
            all_dates = re.findall(r'\d{4}-\d{2}-\d{2}', str(response.xpath('//div[@class="datelist"]/ul/text()')))
            for date in all_dates:
                if cmp(date,self.endDate) < 0:
                    self.pageControl[stock_code] = "Stop"
        
        if self.pageControl.has_key(stock_code) and self.pageControl[stock_code] == "Next":
            page=int(response.url[-1])+1
            url=('http://vip.stock.finance.sina.com.cn/corp/view/vCB_AllNewsStock.php?symbol=sh%s&Page=1'+str(page) % stock_code)
            request = scrapy.Request(url, callback=self.parse)
            yield request
        
        stock_name=response.xpath("//div[@class='hq_title']/a[4]/h1[@id='stockName']/text()").extract()[0]
        
        for sel in response.xpath('//div[@class="datelist"]/ul/a'):
            url = sel.xpath('@href').extract()[0]
            if self.redis_conn.zscore(RedisKeys.sina_individual_crawled, url) is not None and \
                self.endDate is not None:
                self.logger.debug('url has benn got: '+url)
                continue
            
            if self.redis_conn.zscore(RedisKeys.sina_individual_crawled, url) is not None and \
                self.endDate is None:
                self.logger.debug('url has benn got: '+url)
                break
            
            item = NewsItem()
            item['url'] = url
            item['code'] = stock_code
            item['name'] = stock_name
            title= sel.xpath('text()').extract()[0]
            item['title'] =title
            self.logger.debug("get article url %s" % url)
            request = scrapy.Request(url, callback=self.parse_article)
            request.meta['item'] = item
            
            yield request


    def parse_article(self, response):
        item = response.meta['item']
        item['crawl_ts']=TimeUtils.getCurrentTimeStamp()
        # retrieve document body
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        raw = response.xpath('//*[@id="artibody"]').extract()[0]
        if raw.find(u"原始正文start") !=-1:
            real_content_start=raw.find(u"原始正文start")+13
            raw=raw[real_content_start:].trim()
            
        content = converter.handle(raw)
        item['content'] = content

        # retrieve source
        src_raw = response.xpath('//span[@class="time-source"]').extract()[0]
        src_txt = converter.handle(src_raw).strip()
        source = src_txt.split(" ",1)[1]
        item['article_source']=source
        pub_date= str(datetime.fromtimestamp(mktime(time.strptime(src_txt.replace(u"\xa0", "").replace(" ", "")[:16], u"%Y年%m月%d日%H:%M"))))
        item['pub_date']= pub_date
        self.logger.info('pub_date: '+ item['pub_date'])
        yield item
