# coding: utf-8
import copy
import re, os.path, time, urllib.parse

from App.common.webRequest import WebRequest
from Configs import defaultApp
from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis
from App.service.system.logService import logService
from App.model.crawl.channels.cc1688CrawlRedis import cc1688CrawlRedis
from scrapy.selector import Selector
from App.common.url.baseUrlHandle import baseUrlHandle
import json, gevent
from App.service.system.classContextService import classContextService
from lxml import etree

from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent

import hashlib
import datetime
import elasticsearch

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''



class ccShopeeCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Shopee'

    country = 'th'

    """
     # 设置对象
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:56:10
    """

    def setRelayServiceClass(self, relayServiceClass):
        if not relayServiceClass:
            return False
        if not self.relayServiceClass:
            self.relayServiceClass = relayServiceClass

    def execTask(self):
        taskInfo = self.relayServiceClass.taskPool[self.channleName][self.country]
        for taskInfoIndex in taskInfo:
            for i in range(taskInfo[taskInfoIndex]['execNum']):
                getattr(self, taskInfoIndex)()




            # print(self.taskInfoIndex())


        # self.getEsSalesDataPushRedis()
        # self.consumerSalesDataCrawlerRedis()
        # self.consumerGetCrawlerDataPushEs()
        # self.relayServiceClass.taskPool = 'dsadddass'
        print(12311223)

    """
     # 获取es中有销量的数据，推进redis
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年5月29日 14:54:05
    """
    def getEsSalesDataPushRedis(self):
        print('1111111111getEsSalesDataPushRedis')
        return

    """
     # 监听redis中的数据，采集，并存redis
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年5月29日 14:54:05
    """
    def consumerSalesDataCrawlerRedis(self):
        print('22222222222222consumerSalesDataCrawlerRedis')
        return

    """
     # 监听redis中的采集回来的数据，并存es
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年5月29日 14:54:05
    """
    def consumerGetCrawlerDataPushEs(self):
        print('33333333333consumerGetCrawlerDataPushEs')
        return

    def resetClassVar(self):
        return