# coding: utf-8
import re
from time import sleep
from App.common.webRequest import WebRequest

'''
 # coderbusy
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月5日 14:01:16
 # @version     0.1.0 版本号
'''


class ppProxyCoderBusy(object):
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
        'https://proxy.coderbusy.com/zh-hans/ops/country/cn.html',
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
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                proxy = '{}:{}'.format("".join(tr.xpath("./td[1]/text()")).strip(),
                                       "".join(tr.xpath("./td[2]//text()")).strip())
                if proxy:
                    self.proxyIpPortList.append(proxy)
                    # yield proxy

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return self.proxyIpPortList

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
