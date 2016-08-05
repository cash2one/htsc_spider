#-*- coding: UTF-8 -*-

import sys
import os                                                                                                                               
from os.path import dirname
path = dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(path)


from hbase.hbaseApi import HBaseAPI


api = HBaseAPI()
client=api.getClient()
dict={}
columnFamily='stock'
startRowKey='000000'
#rows=api.getRows(client,tableName='stock_list',columns=['stock:type','stock:name'],startRowKey=startRowKey,numRows=10000)
#for result in rows:
#    columns=result.columns
#    for key,cell in columns.items():
 #       print 'key:'+key
  #      print 'value:'+cell.value


#api.putRow(client,'stock_list',"6000004",{'stock:name': '中国银行','stock:type':'SHA'})

fp=open('/opt/scrapy-project/tools/stock_B.txt') 
for line in  fp.readlines():
    #print line.strip().split(' ')
    text=line.strip()
    text=' '.join(line.strip().split())
    result=text.split()
    print 'code: '+result[0]
    print 'name: '+result[1]
    print 'type: '+result[2]
    api.putRow(client,'stock_list',result[0],{'stock:name':result[1],'stock:type':result[2]})
