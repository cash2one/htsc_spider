# -*- coding: utf-8 -*-
import cookielib
import os
import urllib2
import uuid
from warnings import catch_warnings

from PIL import Image
import html2text
import pyocr
import pyocr.builders
import pytesseract
import scrapy

from common.items import NewsItem
from common.utils import TimeUtils


class DongFangSpider(scrapy.Spider):
    name = "dongfang_spider"
    allowed_domains = ["finance.eastmoney.com"]
    start_urls = [
       "http://finance.eastmoney.com/news/ccjdd_1.html"
   ]
    endDate=None
    def __init__(self, *a, **kw):
        if kw.has_key("endDate"):
            self.endDate = kw["endDate"]

    def parse(self, response):
        
        nextPage=True
            
        for sel in response.xpath('//div[@class="list"]/ul/li'):
            item = NewsItem()
            url = sel.xpath('a/@href').extract()[0]            
            title = sel.xpath('a/text()').extract()[0]
            time = sel.xpath('span/text()').extract()[0]+':00'
            if time < self.endDate : 
                nextPage=False
                break
            item['url'] = url
            item['title'] = title
            item['pub_date'] = time
            item['crawl_ts']=TimeUtils.getCurrentTimeStamp()    
            
            self.logger.debug("get article time %s" % time )
            
            request = scrapy.Request(url, callback=self.parse_article)
            request.meta['item'] = item

            yield request
            
            
        if  nextPage is True:
            page = int(response.url[response.url.find("_")+1:len(response.url) - 5]) + 1
            url = ('http://finance.eastmoney.com/news/ccjdd_' + str(page) + '.html')
            
            self.logger.debug("get nextPage url %s" % url)
            request = scrapy.Request(url, callback=self.parse)
            yield request
            
            
    def parse_article(self, response):

        item = response.meta['item']
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        raw = response.xpath('//div[@id="ContentBody"]').extract()[0]
        content = converter.handle(raw)
        item['content'] = content       
        img_url = response.xpath('//div[@class="Info"]/*/img/@src').extract()[0]
        txt=self.save_file("E:\\img",img_url[img_url.rindex("/")+1:len(img_url)],self.get_file(img_url))
        item["article_source"]=self.jiexi(txt)
        self.logger.debug("get img_url url %s" % txt)

        yield item
    def jiexi(self,source):
        source=source.replace(" ","")
        source=source.replace(u"怔",u"证")
        
        if source.find(u"日经济新"):
            source=u"每日经济新闻"
        elif source.find(u"东方财"):
            source=u"东方财富网"
            
        elif source.find(u"财官中文网"):
            source=u"财富中文网"
        elif source.find(u"毅资懊报"):
            source=u"投资快报"
        elif source.find(u"店讯"):
            source=u"腾讯"
            
        elif source.find(u"华亘时报"):
            source=u"华夏时报"
        elif source.find(u"汇谭网"):
            source=u"汇通网"
        elif source.find(u"凤回网"):
            source=u"凤凰网"
        return source
    def get_file(self,url):
        try:
            cj = cookielib.LWPCookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)

            req = urllib2.Request(url)
            operate = opener.open(req)
            data = operate.read()
            return data
        except BaseException, e:
            print e
            return None
            
    def mkdir(self,path):
        path=path.strip()
        path=path.rstrip("\\")

        if not os.path.exists(path):
            os.makedirs(path)
            
        return path
        
        
        
    def save_file(self,path, file_name, data):
        if data is None:
            return ""
        
        self.mkdir(path)
        if(not path.endswith("/")):
            path=path+"/"
        files = os.listdir(path)
        for name in files:
            if name==file_name:
                return self.parse_image(path+file_name)
            
            
            
       
        file=open(path+file_name, "wb")
        file.write(data)
        file.flush()
        file.close()
        return self.parse_image(path+file_name)
        
        
    def parse_image(self,filepath):
        try:
            tools = pyocr.get_available_tools()[:]
            if len(tools) == 0:
                print("No OCR tool found")
           
            tool = tools[0]
            txt = tool.image_to_string(
                Image.open(filepath),
                lang="chi_sim",
                builder=pyocr.builders.TextBuilder(7)
            )
            if txt is None:
                txt="null"
                
            return txt
        except Exception , e:
            print e
            return "null"
