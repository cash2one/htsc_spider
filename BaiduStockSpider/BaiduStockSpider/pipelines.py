# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from time import sleep
from scrapy_redis.connection import get_redis_conn 
import logging
from avrotools.avro_utils import AvroUtils
from common.config import SpiderSourceCode,SpiderSourceName,kafka_producer,kafkaTopic,RedisKeys
import shortuuid
class BaidustockspiderPipeline(object):
    logger = logging.getLogger("htsc")
    
    def process_item(self, item, spider):
        item["id"] = shortuuid.uuid()
        item["source"]=SpiderSourceName.baidu
        item["type"]=SpiderSourceCode.baidu_stock_opinion
        
        #contents=AvroUtils.createAvroMemoryRecord(item,AvroUtils.getConsensusSchema())
        #kafka_producer.send(kafkaTopic.consensus,value=contents)
        
        self.logger.info("send data to kafka, from "+item["source"] +" , batch: "+str(item["batch"]))
        #sleep(1)
        get_redis_conn().zadd(RedisKeys.baidu_opinion_crawled+str(item["flag"]),item['pub_date'],item['pub_date'])
        return item
    

        
