# -*- coding: utf-8 -*-

import scrapy

class BaiduStockOpinionItem(scrapy.Item):
    id = scrapy.Field()
    type = scrapy.Field()  # 001 individual stoock ,003 baidu opinion 
    source = scrapy.Field()  # like sina,baidu
    pub_date = scrapy.Field()
    batch = scrapy.Field()
    crawl_ts = scrapy.Field()
    code =scrapy.Field()
    name = scrapy.Field()
    rank = scrapy.Field()
    keywords=scrapy.Field()
    flag=scrapy.Field()
    
class NewsItem(scrapy.Item):
    id = scrapy.Field()
    type = scrapy.Field()  # 001 individual stoock ,003 baidu opinion 
    source = scrapy.Field() # like sina,baidu
    scope = scrapy.Field()
    crawl_ts = scrapy.Field()
    pub_date = scrapy.Field()
    code = scrapy.Field()
    name =scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    article_source = scrapy.Field()
    content = scrapy.Field()
    
class XueQiuItem(scrapy.Item):
    id = scrapy.Field()
    type = scrapy.Field()  # 001 individual stoock ,003 baidu opinion 
    source = scrapy.Field() # like sina,baidu,xueqiu
    scope = scrapy.Field()
    crawl_ts = scrapy.Field()
    pub_date = scrapy.Field()
    code = scrapy.Field()
    name =scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    article_source = scrapy.Field()
    content = scrapy.Field()
    
class CommentItem(scrapy.Item):
    id = scrapy.Field()  #shortuuid
    crawl_ts = scrapy.Field()
    username = scrapy.Field()
    content = scrapy.Field()
    pub_date = scrapy.Field()
    

'''
class SinaItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    date = scrapy.Field()
    body = scrapy.Field()
    source = scrapy.Field()
    channel = scrapy.Field()
    newsid = scrapy.Field()
    comments = scrapy.Field()
    crawl_ts = scrapy.Field()
'''