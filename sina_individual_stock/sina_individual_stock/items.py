# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy.loader.processors import MapCompose, TakeFirst, Join



class SinaIndividualStockItem(scrapy.Item):
    code = scrapy.Field()
    name =scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    pub_date = scrapy.Field()
    source = scrapy.Field()
    channel = scrapy.Field()
    newsid = scrapy.Field()
    comments = scrapy.Field()
    crawl_ts = scrapy.Field()

class SinaItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    date = scrapy.Field()
    body = scrapy.Field()
    source = scrapy.Field()
    channel = scrapy.Field()
    newsid = scrapy.Field()
    comments = scrapy.Field(serializer=str)
    crawl_ts = scrapy.Field()










