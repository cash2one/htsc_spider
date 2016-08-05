# -*- coding: utf-8 -*-

import logging
import scrapy
import html2text
from scrapy_redis.connection import get_redis_conn
from common.config import RedisKeys
from common.items import CommentItem
from common.utils import TimeUtils

class XueQiuCommentSpider(scrapy.Spider):
    name = "xueqiu_comment_spider"
    start_urls = ["https://xueqiu.com/hq"]
    logger = logging.getLogger("htsc")
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
               #"cookie":"s=17oq11ispk; bid=51bf343af0b5db58fa6e93dcfd40f32b_iqheqevn; webp=0; last_account=liujinliang99%40gmail.com; __utma=1.688519314.1468203981.1468809783.1468827169.9; __utmz=1.1468203981.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); xq_a_token=8ad8a3fb388253fb1fbd474babca71698376e32e; xq_r_token=855758ef5a357efb7a6ac2984a06f4e5fca12016; Hm_lvt_1db88642e346389874251b5a1eded6e3=1468206099,1468289434,1468373638,1469068325; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1566068686", \
               "cache-control": "no-cache"
              }
    
    def parse(self, response):
        access_token_list = response.xpath('//script').re('SNB.data.access_token.*\|\| "(.*)";')
        if len(access_token_list) == 0:
            self.logger.error("get access_token error")
            return
        
        self.headers["cookie"]="xq_a_token="+access_token_list[0]
        
        self.redis_conn=get_redis_conn()
        xueqiu_comment_relation=self.redis_conn.zrange(RedisKeys.xueqiu_comment_relation, start=0, end=-1, desc=False, withscores=True)
        #get all data, if want to get part of redis, use zrangebyscore
        for relation in xueqiu_comment_relation:  #id&user_id&uuid
            result=relation[0].split("&&")
            self.logger.info("article corelation:"+str(result))
            user_id=result[0]
            article_id=result[1]
            article_hive_id=result[2]  # shortuuid ,to construct mapping with articles
            comment_url="https://xueqiu.com/service/comment/list?id="+article_id+"&user_id="+user_id+"&type=status&sort=false&page=1"
            request = scrapy.Request(comment_url,headers=self.headers,callback=self.parse_comment)
            request.meta["article_hive_id"]=article_hive_id
            request.meta["article_id"]=article_id
            request.meta["user_id"]=user_id
            yield request
        
        
    def parse_comment(self, response):
        print "parse_comment, url: "+response.url
        article_hive_id=response.meta["article_hive_id"]
        nextPage=True
        
        respons_xpath=response.xpath("//div[@class='comment-mod-bd']/div[@*]")
        if len(respons_xpath) == 0 :  #last page
            return
        
        for sel in respons_xpath:
            item=CommentItem()
            comment_id=sel.xpath('@id').extract()[0][8:]
            print "comment_id:"+comment_id
            item["id"]=article_hive_id+"&&"+comment_id
            
            if self.redis_conn.zscore(RedisKeys.xueqiu_comment_crawled, comment_id) is not None:
                nextPage=False
                print "nextPage=False"
                break
            
            userName=sel.xpath("div[@class='comment-item-bd']/h4/a[@class='name']/text()").extract()[0]
            item["username"]=userName
            comment_content=sel.xpath("div[@class='comment-item-bd']/div[@class='comment-item-content']").extract()[0]   #div[@class='detail']/i
            converter = html2text.HTML2Text()
            converter.ignore_links = True
            comment_content = converter.handle(comment_content)
            item["content"]=comment_content
        
            comment_pub_date=sel.xpath("div[@class='comment-item-ft']/div[@class='comment-meta']/div[@class='meta-info']/span[@class='time']/text()").extract()[0]
            #print "comment_pub_date original:"+comment_pub_date
            if comment_pub_date.find(u"今天") != -1: #今天 17:24
                comment_pub_date=TimeUtils.getCurrentDate()+comment_pub_date[2:]+":00"
            elif comment_pub_date.find(u"分钟前") != -1:
                minute_before=comment_pub_date[0:comment_pub_date.find(u"分钟前")]
                comment_pub_date = TimeUtils.getDateSubtractMinutes(int(minute_before))
            else: #07-13 14:08
                comment_pub_date=TimeUtils.getCurrentYear()+"-"+comment_pub_date+":00"
            
            item["pub_date"]=comment_pub_date
            item['crawl_ts']=TimeUtils.getCurrentTimeStamp()
            
            #print "userName: "+userName
            #print "comment_content: "+comment_content
            print "comment_pub_date: "+comment_pub_date
            self.logger.info("comment_pub_date:"+comment_pub_date)
            
            yield item
            
        if nextPage == True:
            page=int(response.url[-1])+1
            article_id=response.meta["article_id"]
            user_id=response.meta["user_id"]
            comment_url="https://xueqiu.com/service/comment/list?id="+article_id+"&user_id="+user_id+"&type=status&sort=false&page="+str(page)
            request = scrapy.Request(comment_url,headers=self.headers,callback=self.parse_comment)
            request.meta["article_hive_id"] = article_hive_id
            request.meta["article_id"]=article_id
            request.meta["user_id"]=user_id
            yield request
        
