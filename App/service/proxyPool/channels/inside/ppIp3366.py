# coding: utf-8
import re
from App.common.webRequest import WebRequest

'''
 # 无忧
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月5日 14:01:16
 # @version     0.1.0 版本号
'''


class ppIp3366(object):
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
        'http://www.ip3366.net/free/?stype=1&page=1',
        'http://www.ip3366.net/free/?stype=2&page=1'
    ]

    key = 'ABCDEFGHIZ'

    """
    # 键值
    # @var string  
    """
    page = 3

    """
     # 无忧代理
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """

    def getProxyResult(self):
        for url in self.targetUrls:
            # for page in range(1, self.page):
            # url = url.format(page)
            # url = url + 1
            result = WebRequest().get(url, timeout=10)
            regularCode = r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>'
            proxies = re.findall(regularCode, result.text())
            for proxy in proxies:
                self.proxyIpPortList.append(":".join(proxy))

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return self.proxyIpPortList

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
