# -*- coding: utf-8 -*-

import datetime
import time
import re


class TimeUtils(object):
    @staticmethod
    def getCurrentTimeStamp():
        return time.strftime( '%Y-%m-%d %X', time.localtime(time.time()))
    
    @staticmethod
    def getTodayDaybreak():
        '''
        return date str like 2016-07-18 00:00:00
        '''
        return time.strftime( '%Y-%m-%d 00:00:00', time.localtime(time.time()))
    
    @staticmethod
    def getCurrentDate():
        return time.strftime( '%Y-%m-%d', time.localtime(time.time()))
    
    @staticmethod
    def getCurrentYear():
        return time.strftime( '%Y', time.localtime(time.time()))
    
    @staticmethod
    def getDateSubtractMinutes(mins):
        d1 = datetime.datetime.now()
        d2 = d1 - datetime.timedelta(minutes=mins)
        return str(d2)[0:19]
    
    @staticmethod
    def isValidEndDate(endDate):
        '''
        format like 2016-01-01
        '''
        result = re.findall(r'^\d{4}-\d{2}-\d{2}$', endDate)
        return len(result) != 0
    
   
    