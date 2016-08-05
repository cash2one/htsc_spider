#! /bin/bash

basepath=$(cd `dirname $0`; pwd)
htsc_home=`dirname $basepath`
spider_home=$htsc_home"/BaiduStockSpider"
 
cd $spider_home
scrapy crawl -a batch=$1 baidu_opinion_spider &