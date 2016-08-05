# -*- coding: utf-8 -*-


import os.path                                                                                               
from os.path import dirname
import logging
root_path = dirname(os.path.abspath(dirname(__file__)))

from kafka import KafkaProducer

logging.config.fileConfig(root_path+"/common/logging.conf")
logger = logging.getLogger("htsc")
  
class GlobalConfig(object):
    redis_server='localhost'
    redis_server_port=6379
    project_home=root_path+"/"
    #kafka_bootstrap_servers="168.9.99.33:9092"
    kafka_bootstrap_servers="192.168.99.100:9092"
    
    max_times_error_before_changeIP=300
    log_htsc_key="htsc"

try:
    kafka_producer=None
    #kafka_producer = KafkaProducer(bootstrap_servers=GlobalConfig.kafka_bootstrap_servers)
except Exception, e:
    logger.error("cant not connect to kafka")
    
class SpiderSourceCode(object):
    individual_stock="001"
    baidu_stock_opinion="003"
    xueqiu="002"
    dongfang="004"
    
# source
class SpiderSourceName(object):
    baidu="baidu"
    sina="sina"
    xueqiu="xueqiu"
    dongfang="dongfang"
    
class kafkaTopic(object):
    consensus="sp_consensuses"  #sp_consensus
    news="sp_news"
    comments="sp_comments"

class RedisKeys(object):
    baidu_opinion_crawled="baidu_opinion_has_crawled_date"
    sina_individual_crawled="sina_individual_stock_url_crawled"
    xueqiu_url_crawled="xueqiu_url_crawled"
    xueqiu_comment_relation="xueqiu_comment_relation"  #id&user_id&uuid
    xueqiu_comment_crawled="xueqiu_comment_crawled"
    SHAStockCode="SHAStockCode"
    dongfang_url_crawl="dongfang_url_crawl"
    
    
