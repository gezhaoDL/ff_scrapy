# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
from .utils import *
import logging
import base64
import random
import json
# api_url = "http://dps.kdlapi.com/api/getdps/?orderid=997897358124255&num=1&pt=1&format=json&sep=1"
username = ""
password = ""
api_key = ''
order_id = ''
api_url = "http://dps.kdlapi.com/api/getdps/?orderid={}&num=1&pt=1&format=json&sep=1".format(order_id)
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.internet import defer
from twisted.web.client import ResponseFailed
from scrapy.core.downloader.handlers.http11 import TunnelError
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from scrapy import signals


class ScrapyProjectSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.
    logger.info('ScrapyProjectSpiderMiddleware')

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        logger.info('process_spider_input')
        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.
        logger.info('process_spider_output')
        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.
        logger.info('process_spider_exception')
        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.
        logger.info('process_start_requests')
        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyProjectDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                          ConnectionRefusedError, ConnectionDone, ConnectError,
                          ConnectionLost, TCPTimedOutError, ResponseFailed,
                          IOError, TunnelError)
        logging.info('DownloaderMiddleware initing')
        self.proxies,self.proxy_ip = get_proxies()
        #self.proxy_ip=requests.get(api_url).json()['data']['proxy_list'][0]
        self.req_time=0
        logging.info('proxy_ip  %s',self.proxy_ip)

        self.user_agent_list =\
            ['Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6',
    'Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6',
    'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.3 Mobile/14E277 Safari/603.1.30',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
             ]
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        request.headers['User-Agent']=random.choice(self.user_agent_list)
        #request.headers['User-Agent']='Mozilla/5.0'
        logger.info('request url %s', request.url)
        #logger.info('request meta %s', request.meta)
        # logger.info('set random Agent %s', request.headers)
        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        logging.info('process request...')
        if self.req_time==150:
            self.req_time=0
            proxies,proxy_ip = get_proxies()
        else:
            proxy_ip = get_valid_ip(self.proxy_ip)
        self.proxy_ip=proxy_ip
        if request.url.startswith("http://"):
            request.meta['proxy'] = "http://{proxy_ip}".format(proxy_ip=get_valid_ip(proxy_ip))
        elif request.url.startswith("https://"):
            request.meta['proxy'] = "https://{proxy_ip}".format(proxy_ip=get_valid_ip(proxy_ip))
        # 使用私密代理或独享代理需要将用户名和密码进行base64编码，然后赋值给request.headers["Proxy-Authorization"]
        #
        # 如果是开放代理就不需要以下步骤，直接设置代理IP即可
        user_password = "{username}:{password}".format(username=username, password=password)
        b64_user_password = base64.b64encode(user_password.encode("utf-8"))
        request.headers["Proxy-Authorization"] = "Basic " + b64_user_password.decode("utf-8")
        self.req_time=self.req_time + 1
        logging.info("using proxy: {} req_times {}".format(request.meta['proxy'],self.req_time))
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        logging.info('process_response...response %s',response.status)
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        if isinstance(exception, self.ALL_EXCEPTIONS):
            logger.error("[Got exception]   {}".format(exception))
            request.headers['User-Agent'] = random.choice(self.user_agent_list)
            #request.headers['User-Agent'] = 'Mozilla/5.0'
            proxies, proxy_ip = get_proxies()
            self.proxy_ip = proxy_ip
            return request


    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
