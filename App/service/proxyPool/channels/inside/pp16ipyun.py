# coding: utf-8
import re, json
from time import sleep
from App.common.webRequest import WebRequest
from App.service.system.classContextService import classContextService
from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis

'''
 # xicidaili
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月5日 14:01:16
 # @version     0.1.0 版本号
'''


class pp16ipyun(object):
    """
    # 抓取结果集
    # @var string
    """
    proxyIpPortList = []

    """
    # 获取IP数量
    # @var string
    """
    getNum = 50

    """
     # iphai
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月5日 14:12:36
    """

    def getProxyResult(self):
        proxyUrl = 'http://ip.16yun.cn:817/myip/pl/d34c6d12-ce51-492e-b372-c3d8751c3e29/?s=lmxrbkovdm&u=garydjd&format=json&count={}'.format(self.getNum)
        proxyResult = WebRequest.easyGet(self=WebRequest, url=proxyUrl)
        proxies = proxyResult.text(self=WebRequest)
        print(proxies)
        if not proxies:
            return
        proxiesDict = json.loads(proxies)
        if proxiesDict:
            if proxiesDict['proxy']:
                for i in proxiesDict['proxy']:
                    classContextService().setListVarByNameValue(name=self.__class__.__name__ + '_proxyPp16ipyunIpPortList', value=i['ip'] + ':' + str(i['port']))

    def saveProxyIpPortList(self):
        proxyIpPortList = classContextService().getVarByName(name=self.__class__.__name__ + '_proxyPp16ipyunIpPortList')
        for ProxyIpPortKey in proxyIpPortList:
            proxyPoolRedis().increasePayProxyPool(ProxyIpPortKey)

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return classContextService().getVarByName(name=self.__class__.__name__ + '_proxyPp16ipyunIpPortList')

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
