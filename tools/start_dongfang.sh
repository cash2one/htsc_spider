#! /bin/bash

basepath=$(cd `dirname $0`; pwd)
htsc_home=`dirname $basepath`
spider_home=$htsc_home"/DongFang"

cd $spider_home
scrapy crawl dongfang_spider &