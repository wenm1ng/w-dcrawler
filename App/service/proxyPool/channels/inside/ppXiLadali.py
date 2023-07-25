# coding: utf-8
import re
from time import sleep
from App.common.webRequest import WebRequest
from App.service.system.classContextService import classContextService

'''
 # xicidaili
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月5日 14:01:16
 # @version     0.1.0 版本号
'''


class ppXiLadali(object):
    """
    # 抓取结果集
    # @var string
    """
    proxyIpPortList = []

    """
    # 抓取目标连接
    # @var string  
    """
    targetUrls = [
        # 'http://www.xiladaili.com/putong/',
        "http://www.xiladaili.com/gaoni/",
        "http://www.xiladaili.com/http/",
        "http://www.xiladaili.com/https/"
    ]

    """
    # 页面
    # @var int  
    """
    page = 2

    """
     # iphai
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月5日 14:12:36
    """

    def getProxyResult(self):
        for url in self.targetUrls:
            r = WebRequest().get(url, timeout=10)
            regularCode = r'\d+.\d+.\d+.\d+:\d+'
            #ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", r.text)
            ips = re.findall(regularCode, r.text())
            for ip in ips:
                classContextService().setListVarByNameValue(name=self.__class__.__name__ + '_proxyIpPortList', value=ip.strip())
                # yield ip.strip()

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return classContextService().getVarByName(name=self.__class__.__name__ + '_proxyIpPortList')

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
