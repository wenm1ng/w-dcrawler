# coding: utf-8
import re
from App.common.webRequest import WebRequest

'''
 # jiangxianli
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月5日 14:01:16
 # @version     0.1.0 版本号
'''


class ppJiangxianli(object):
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
        'http://ip.jiangxianli.com/?country=中国&page={}',
    ]

    countryMap = [
        '中国',
        '香港',
        '伊拉克',
        '俄罗斯联邦',
        '加拿大',
        '印度尼西亚',
        '孟加拉',
        '德国',
        '新加坡',
        '日本',
        '法国',
        '瑞典',
        '美国',
        '阿富汗',
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
        for i in range(1, 2):
            url = self.targetUrls[0].format(i)
            html_tree = WebRequest().get(url).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                self.proxyIpPortList.append(":".join(tr.xpath("./td/text()")[0:2]).strip())
                # yield ":".join(tr.xpath("./td/text()")[0:2]).strip()


    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return self.proxyIpPortList

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass
