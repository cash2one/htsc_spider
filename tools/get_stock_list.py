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
rows=api.getRows(client,tableName='stock_list',columns=['stock:type','stock:name'],startRowKey=startRowKey,numRows=10000)
for result in rows:
    columns=result.columns
    for key,cell in columns.items():
        print 'key:'+key
        print 'value:'+cell.value
