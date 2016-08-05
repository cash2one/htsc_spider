# -*-coding:utf-8-*-

from twisted.internet.error import ConnectionRefusedError,TCPTimedOutError,\
ConnectionLost,TimeoutError,ConnectError

from common.config import GlobalConfig
import logging
import os

class MyProxyMiddleware(object):
    logger = logging.getLogger("htsc")
    error_count=0;
    
    def process_exception(self,request, exception, spider):
        if  isinstance(exception,ConnectionRefusedError) or \
            isinstance(exception,TCPTimedOutError) or \
            isinstance(exception,ConnectionLost) or \
            isinstance(exception,TimeoutError) or \
            isinstance(exception,ConnectError):
            
            self.error_count +=1
            if(self.error_count>GlobalConfig.max_times_error_before_changeIP):
                #change ip
                change_ip_response = os.popen("python /home/appadmin/eip/py/eip.py")
                self.logger.debug(change_ip_response.read())
                change_ip_response.close()
                self.error_count=0
                
            return request  #rescheduled to be downloaded in the future
        
    
