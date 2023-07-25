# coding: utf-8
import re
from time import sleep
from App.common.webRequest import WebRequest

'''
 # xicidaili
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月5日 14:01:16
 # @version     0.1.0 版本号
'''


class ppXicidali(object):
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
        'http://www.xicidaili.com/nn/',  # 高匿
        'http://www.xicidaili.com/nt/',  # 透明
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
        for each_url in self.targetUrls:
            for i in range(1, self.page + 1):
                page_url = each_url + str(i)
                tree = WebRequest().get(page_url).tree
                proxy_list = tree.xpath('.//table[@id="ip_list"]//tr[position()>1]')
                for proxy in proxy_list:
                    try:
                        self.proxyIpPortList.append(':'.join(proxy.xpath('./td/text()')[0:2]))
                        # yield ':'.join(proxy.xpath('./td/text()')[0:2])
                    except Exception as e:
                        pass

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return self.proxyIpPortList

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
