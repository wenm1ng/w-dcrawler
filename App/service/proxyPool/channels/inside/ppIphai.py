# coding: utf-8
import re
from App.common.webRequest import WebRequest

'''
 # 无忧
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月5日 14:01:16
 # @version     0.1.0 版本号
'''


class ppIphai(object):
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
        'http://www.iphai.com/free/ng',
        'http://www.iphai.com/free/np',
        'http://www.iphai.com/free/wg',
        'http://www.iphai.com/free/wp'
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
            proxies = re.findall(
                r'<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>',
                r.text)
            for proxy in proxies:
                # yield ":".join(proxy)
                self.proxyIpPortList.append(":".join(proxy))

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return self.proxyIpPortList

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
