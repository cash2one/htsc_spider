#! /bin/bash

basepath=$(cd `dirname $0`; pwd)
htsc_home=`dirname $basepath`
spider_home=$htsc_home"/sina_individual_stock"

cd $spider_home
scrapy crawl sina_individual_stock_spider &