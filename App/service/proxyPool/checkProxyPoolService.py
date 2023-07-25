# coding: utf-8


import requests
'''
 # 首页控制器
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class checkProxyPoolService(object):

    """
     # json测试
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """

    def checkHttpRequest(self):
        proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
                   'Accept': '*/*',
                   'Connection': 'keep-alive',
                   'Accept-Language': 'zh-CN,zh;q=0.8'}
        try:
            r = requests.head('http://www.baidu.com', headers=headers, proxies=proxies, timeout=10,
                              verify=False)
            if r.status_code == 200:
                return True
        except Exception as e:
            pass
        return False

    pass
