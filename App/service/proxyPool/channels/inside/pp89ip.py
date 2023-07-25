# coding: utf-8
import re
from App.common.webRequest import WebRequest

'''
 # 89ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class pp89ip(object):
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
        'http://www.89ip.cn/index_{}.html',
    ]

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
        for page in range(1, self.page):
            url = self.targetUrls[0].format(page)
            result = WebRequest().get(url, timeout=10)
            regularCode = r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>'
            proxies = re.findall(regularCode, result.text())
            for proxy in proxies:
                self.proxyIpPortList.append(':'.join(proxy))

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return self.proxyIpPortList

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
