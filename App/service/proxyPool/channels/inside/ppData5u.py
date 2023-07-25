# coding: utf-8
import re
from App.common.webRequest import WebRequest

'''
 # 无忧
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月5日 14:01:16
 # @version     0.1.0 版本号
'''


class ppData5u(object):

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
        'http://www.data5u.com/',
        'http://www.data5u.com/free/gngn/index.shtml',
        'http://www.data5u.com/free/gnpt/index.shtml'
    ]

    key = 'ABCDEFGHIZ'

    """
    # 键值
    # @var string  
    """
    page = 2

    """
     # 无忧代理
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """

    def getProxyResult(self):
        for url in self.targetUrls:
            html_tree = WebRequest().get(url).tree
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    ip = ul.xpath('./span[1]/li/text()')[0]
                    classnames = ul.xpath('./span[2]/li/attribute::class')[0]
                    classname = classnames.split(' ')[1]
                    port_sum = 0
                    for c in classname:
                        port_sum *= 10
                        port_sum += self.key.index(c)
                    port = port_sum >> 3
                    # yield '{}:{}'.format(ip, port)
                    self.proxyIpPortList.append('{}:{}'.format(ip, port))
                except Exception as e:
                    print(e)

    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return self.proxyIpPortList

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
