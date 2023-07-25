# coding: utf-8
import re
from App.common.webRequest import WebRequest
from App.service.system.classContextService import classContextService

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class pp66ip(object):
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
        'http://www.66ip.cn/mo.php',
    ]

    """
    # 键值
    # @var string  
    """
    key = 'ABCDEFGHIZ'

    """
     # 无忧代理
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """

    def getProxyResult(self):
        for url in self.targetUrls:
            result = WebRequest().get(url, timeout=10)
            regularCode = r'\d+.\d+.\d+.\d+:\d+'
            proxies = re.findall(regularCode, result.text())
            for proxy in proxies:
                classContextService().setListVarByNameValue(name=self.__class__.__name__ + '_proxyIpPortList', value=proxy)

    def getProxyIpPortList(self):
        return self.proxyIpPortList

    def getProxyList(self):
        return classContextService().getVarByName(name=self.__class__.__name__ + '_proxyIpPortList')

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
