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


class proxyPoolRedis(object):
    freeProxyPoolKey = 'freeProxyPool'
    proxyPoolKey = 'trueProxyPool'
    trueOutsideProxyPool = 'trueOutsideProxyPool'
    incrementNumberStep = 1

    countryFreeProxyPoolKeyMap = {
        '中国': 'freeProxyPool',
        '香港': 'hkFreeProxyPool',
        '伊拉克': 'iraqFreeProxyPool',
        '俄罗斯联邦': 'RussiaFreeProxyPool',
        '加拿大': 'CanadaFreeProxyPool',
        '印度尼西亚': 'IndonesiaFreeProxyPool',
        '孟加拉': 'russiaFreeProxyPool',
        '德国': 'bengalFreeProxyPool',
        '新加坡': 'singaporeFreeProxyPool',
        '日本': 'japanFreeProxyPool',
        '法国': 'franceFreeProxyPool',
        '瑞典': 'swedenFreeProxyPool',
        '美国': 'americaFreeProxyPool',
        '阿富汗': 'afghanistanFreeProxyPool',
    }

    """
     # 新增
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def increaseFreeProxyPool(self, value):
        if not value:
            return False

        return baseRedis().connectRedis().zincrby(name=self.freeProxyPoolKey, amount=self.incrementNumberStep, value=value)

    """
     # 新增
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def increasePayProxyPool(self, value):
        if not value:
            return False

        return baseRedis().connectRedis().zincrby(name=self.proxyPoolKey, amount=self.incrementNumberStep, value=value)

    """
     # 新增
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def increaseTrueOutsideProxyPool(self, value):
        if not value:
            return False

        return baseRedis().connectRedis().zincrby(name=self.trueOutsideProxyPool, amount=self.incrementNumberStep, value=value)

    """
     # 新增
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def delTrueOutsideProxyPool(self):
        return baseRedis().connectRedis().delete(self.trueOutsideProxyPool)

    """
     # 新增
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def delPayProxyPool(self):
        return baseRedis().connectRedis().delete(self.proxyPoolKey)

    """
     # 新增
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def delFreeProxyPool(self):
        return baseRedis().connectRedis().delete(self.freeProxyPoolKey)

    """
     # 新增
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def getRandomNumFreeProxyPool(self, countNum, randomNum):
        if not countNum:
            return False
        if not randomNum:
            return False

        start = abs(randint(0, countNum) - randomNum)
        end = start + randomNum
        return baseRedis().connectRedis().zrange(name=self.freeProxyPoolKey, start=start, end=end)

    def getFreeProxyPoolCount(self):
        return baseRedis().connectRedis().zcard(name=self.freeProxyPoolKey)

    def getRandomNumProxyPool(self, countNum, randomNum):
        if not countNum:
            return False
        if not randomNum:
            return False

        start = randint(0, countNum)
        end = start + randomNum
        return baseRedis().connectRedis().zrange(name=self.proxyPoolKey, start=start, end=end)

    def getProxyPoolCount(self):
        return baseRedis().connectRedis().zcard(name=self.proxyPoolKey)


    def getRandomNumTrueOutsideProxyPool(self, countNum, randomNum):
        if not countNum:
            return False
        if not randomNum:
            return False

        start = randint(0, countNum)
        end = start + randomNum
        return baseRedis().connectRedis().zrange(name=self.trueOutsideProxyPool, start=start, end=end)

    def getTrueOutsideProxyPoolCount(self):
        return baseRedis().connectRedis().zcard(name=self.trueOutsideProxyPool)


    """
     # 设置过期键
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def setexStringByName(self, name):
        if not name:
            return
        return baseRedis().connectRedis().setex(name=name, time=120, value='')

    """
     # 追加
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月21日 10:06:37
    """

    def appendStringByName(self, name, value):
        if not name:
            return
        if not value:
            return
        return baseRedis().connectRedis().append(key=name, value=value)

    """
     # 查找
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月21日 10:41:40
    """

    def getStringByName(self, name):
        if not name:
            return
        return baseRedis().connectRedis().get(name=name)

    pass
