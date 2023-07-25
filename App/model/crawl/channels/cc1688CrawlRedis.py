# coding: utf-8
from random import random, randint

from App.common.model.baseRedis import baseRedis
from Configs import defaultApp
import json

'''
 # 设置代理池
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class cc1688CrawlRedis(object):
    hashKey = 'cc1688CrawlRedisHtml'
    hashResultKey = 'cc1688CrawRedisResult'

    """
     # 新增
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def addHashHtml(self, key, value):
        if not key:
            return False
        if not value:
            return False
        return baseRedis().connectRedis().hset(name='cc1688CrawlRedisHtml', key=key, value=value)

    def getHashHtmlByKey(self, key):
        if not key:
            return False
        return baseRedis().connectRedis().hget(name='cc1688CrawlRedisHtml', key=key)

    """
    #
    # 增加hash result
    # @params key hash key
    # @params value hash value
    # @author foolminx foolminx@163.com
    # Date 2021-01-15 19:44:40
    #
    """
    def addHashResult(self, key, value):
        if not key:
            return False
        if not value:
            return False
        return baseRedis.connectRedis().hset(name=self.hashResultKey, key=key, value=value)

    def getHashResultByKey(self, key):
        if not key:
            return False
        return baseRedis().connectRedis().hget(name=self.hashResultKey, key=key)
    pass
