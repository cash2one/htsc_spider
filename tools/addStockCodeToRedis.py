#-*- coding: UTF-8 -*-

import sys
import os                                                                                                                               
from os.path import dirname
path = dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(path)
#print path


from scrapy_redis.connection import get_redis_conn

conn=get_redis_conn()

fp=open(path+'/tools/SHACode.txt') 
for line in fp.readlines():
    text=line.strip()
    conn.sadd("SHAStockCode",text)

print "add success"
#print text
print 'contents of SHAStockCode'
codes=conn.smembers('SHAStockCode')
for code in codes:
    print code





