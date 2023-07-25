# coding: utf-8
import re
from App.common.webRequest import WebRequest

'''
 # 无忧
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月5日 14:01:16
 # @version     0.1.0 版本号
'''


class ppGoubanjia(object):

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
        'http://www.goubanjia.com/',
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
        url = self.targetUrls[0]
        result = WebRequest().get(url, timeout=10)
        proxy_list = result.xpath('//td[@class="ip"]')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """.//*[not(contains(@style, 'display: none'))
                                                      and not(contains(@style, 'display:none'))
                                                      and not(contains(@class, 'port'))
                                                      ]/text()
                                              """
        for each_proxy in proxy_list:
            try:
                ip_addr = ''.join(each_proxy.xpath(xpath_str))
                port_str = each_proxy.xpath(".//span[contains(@class, 'port')]/@class")[0].split()[-1]
                port = self._parse_port(port_str.strip())
                # yield '{}:{}'.format(ip_addr, int(port))
                self.proxyIpPortList.append('{}:{}'.format(ip_addr, int(port)))
            except Exception:
                pass


    def setPage(self, page=2):
        self.page = page

    def getProxyList(self):
        return self.proxyIpPortList

    def resetClassVar(self):
        self.proxyIpPortList = []

    # port是class属性值加密得到
    def _parse_port(self,port_element):
        port_list = []
        for letter in port_element:
            port_list.append(str(self.key.find(letter)))
        _port = "".join(port_list)
        return int(_port) >> 0x3

    pass
