#! /bin/bash

basepath=$(cd `dirname $0`; pwd)
htsc_home=`dirname $basepath`
spider_home=$htsc_home"/XueQiu"

cd $spider_home
scrapy crawl xueqiu_comment_spider &