# coding: utf-8

import gevent

from App import app
from Configs import defaultApp
import os
import re
import hashlib
from time import sleep
# import requests

from App.common.webRequest import WebRequest

from App.service.proxyPool.channels.inside.pp66ip import pp66ip
from App.service.proxyPool.channels.inside.pp89ip import pp89ip
from App.service.proxyPool.channels.inside.ppGoubanjia import ppGoubanjia
from App.service.proxyPool.channels.inside.ppIphai import ppIphai
from App.service.proxyPool.channels.inside.ppJiangxianli import ppJiangxianli
from App.service.proxyPool.channels.inside.ppIp3366 import ppIp3366
from App.service.proxyPool.channels.inside.ppKuaidaili import ppKuaidaili
from App.service.proxyPool.channels.inside.ppData5u import ppData5u
from App.service.proxyPool.channels.inside.ppProxyCoderBusy import ppProxyCoderBusy
from App.service.proxyPool.channels.inside.ppXicidali import ppXicidali
from App.service.proxyPool.channels.inside.ppXiLadali import ppXiLadali
from App.service.proxyPool.channels.inside.ppZhiMadali import ppZhiMadali
from App.service.proxyPool.channels.inside.ppIpIdea import ppIpIdea
from App.service.proxyPool.channels.inside.pp16ipyun import pp16ipyun

from App.service.proxyPool.channels.outside.ppCnProxy import ppCnProxy
from App.service.proxyPool.channels.outside.ppProxyList import ppProxyList
from App.service.proxyPool.channels.outside.ppProxyListPlus import ppProxyListPlus

from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis

'''
 # 设置代理池
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class setProxyPoolService(object):
    """
    # 当前任务
    # @var []
    """
    checkProxyIpTask = []

    """
     # 欢迎页面
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """

    def getProxyPoolsetPools(self):
        result = False
        if not defaultApp.allowProxyDict:
            return False

        customRedisfunction = [
            'ppZhiMadali',
            'ppIpIdea',
            'pp16ipyun',
        ]

        # monkey.patch_all()
        globalObject = globals()
        proxyPoolRedis().delPayProxyPool()
        proxyPoolRedis().delFreeProxyPool()
        proxyPoolRedis().delTrueOutsideProxyPool()
        for environmentKey in defaultApp.allowProxyDict:
            if environmentKey == defaultApp.runningServerLocation:
                for environmentKeyKey in defaultApp.allowProxyDict[environmentKey]:
                    payProxy = False
                    if environmentKeyKey not in globalObject.keys():
                        continue

                    if environmentKeyKey in customRedisfunction:
                        payProxy = True
                    classObject = globalObject[environmentKeyKey]
                    classObject.getProxyResult(classObject)
                    proxyIpPortList = classObject.getProxyList(classObject)
                    if not proxyIpPortList:
                        continue
                    if payProxy:
                        classObject.saveProxyIpPortList(classObject)
                        # for ProxyIpPortKey in proxyIpPortList:
                        #     proxyPoolRedis().increasePayProxyPool(ProxyIpPortKey)
                    else:
                        for ProxyIpPortKey in proxyIpPortList:
                            # 发起请求
                            self.checkProxyIpTask.append(gevent.spawn(self.checkProxyTrueIp, ip=ProxyIpPortKey))
                        res = gevent.joinall(self.checkProxyIpTask)
                        self.checkProxyIpTask = []
                    classObject.resetClassVar(classObject)

    """
     # 简易判断请求头部版本
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月15日 14:32:27
    """

    def checkProxyIp(self, ip):
        result = None
        if not ip:
            return result
        result = WebRequest().easyGetHead('http://www.baidu.com', timeout=10, proxies={
            'http': 'http://{}'.format(ip),
            'https': 'https://{}'.format(ip)
        })

        return result.statusCode()

    """
     # 判断请求头部版本
     # @param self
     # @param ip
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月15日 14:32:27
    """

    def checkProxyTrueIp(self, ip):
        result = None
        if not ip:
            return result
        result = WebRequest().easyGetHead('http://www.baidu.com', timeout=10, proxies={
            'http': 'http://{}'.format(ip),
            'https': 'https://{}'.format(ip)
        })
        if result.statusCode() == 200:
            proxyPoolRedis().increaseFreeProxyPool(ip)
        return True

    pass
