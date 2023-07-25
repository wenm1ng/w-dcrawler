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


class ppZhiMadali(object):
    """
    # 抓取结果集
    # @var string
    """
    proxyIpPortList = []

    """
    # 获取IP数量
    # @var string
    """
    getNum = 1400

    """
     # iphai
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月5日 14:12:36
    """

    def getProxyResult(self):
        proxyUrl = 'http://webapi.http.zhimacangku.com/getip?num={}&type=2&pro=&city=0&yys=0&port=1&pack=115750&ts=0&ys=0&cs=0&lb=6&sb=,&pb=4&mr=1&regions='.format(self.getNum)
        proxyResult = WebRequest.easyGet(self=WebRequest, url=proxyUrl)
        proxies = proxyResult.text(self=WebRequest)
        if not proxies:
            return
        proxiesDict = json.loads(proxies)
        if proxiesDict:
            if proxiesDict['data']:
                for i in proxiesDict['data']:
                    classContextService().setListVarByNameValue(name=self.__class__.__name__ + '_proxyPpZhiMadaliIpPortList', value=i['ip'] + ':' + str(i['port']))

    def saveProxyIpPortList(self):
        proxyIpPortList = classContextService().getVarByName(name=self.__class__.__name__ + '_proxyPpZhiMadaliIpPortList')
        for ProxyIpPortKey in proxyIpPortList:
            proxyPoolRedis().increasePayProxyPool(ProxyIpPortKey)

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return classContextService().getVarByName(name=self.__class__.__name__ + '_proxyPpZhiMadaliIpPortList')

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
