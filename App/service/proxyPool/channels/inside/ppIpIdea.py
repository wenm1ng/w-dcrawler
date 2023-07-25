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


class ppIpIdea(object):
    """
    # 抓取结果集
    # @var string
    """
    proxyIpPortList = []

    """
    # 获取IP数量
    # @var string
    """
    getNum = 500

    """
     # iphai
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月5日 14:12:36
    """

    def getProxyResult(self):
        proxyUrl = 'http://tiqu.linksocket.com:81/abroad?num={}&type=2&lb=1&sb=0&flow=1&regions=us&port=1&n=0'.format(self.getNum)
        proxyResult = WebRequest.easyGet(self=WebRequest, url=proxyUrl)
        proxies = proxyResult.text(self=WebRequest)
        if not proxies:
            return
        proxiesDict = json.loads(proxies)
        if proxiesDict:
            if proxiesDict['data']:
                for i in proxiesDict['data']:
                    classContextService().setListVarByNameValue(name=self.__class__.__name__ + '_proxyPpIpIdeaPortList', value=i['ip'] + ':' + str(i['port']))

    def saveProxyIpPortList(self):
        proxyIpPortList = classContextService().getVarByName(name=self.__class__.__name__ + '_proxyPpIpIdeaPortList')
        for ProxyIpPortKey in proxyIpPortList:
            proxyPoolRedis().increaseTrueOutsideProxyPool(ProxyIpPortKey)

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return classContextService().getVarByName(name=self.__class__.__name__ + '_proxyPpIpIdeaPortList')

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
