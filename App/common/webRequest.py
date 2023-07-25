# coding: utf-8

from requests.models import Response
import requests, json
import random
import time
from lxml import etree
from App.service.system.logService import logService

requests.packages.urllib3.disable_warnings()

'''
 # 封装请求
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月7日 16:24:18
 # @version     0.1.0 版本号
'''


class WebRequest(object):

    def __init__(self, *args, **kwargs):
        self.response = Response()

    """
     # 设置UA
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def user_agent(self):
        """
        return an User-Agent at random
        :return:
        """
        ua_list = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
            'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
        ]
        return random.choice(ua_list)

    """
     # 设置请求头
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    @property
    def header(self):
        return {'User-Agent': self.user_agent,
                'Accept': '*/*',
                'Connection': 'close',
                # 'range': 'bytes=0-200',
                'cache-control': 'no-cache',
                'Content-Type': 'application/json; charset=UTF-8',
                'Accept-Encoding': 'gzip,deflate,br',
                'Accept-Language': 'zh-CN,zh;q=0.8'
                }

    """
     # 请求
     # @param self
     # @param header    请求头
     # @param retry_time 重试时间
     # @param retry_interval 重试次数
     # @param timeout 超时时间
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def get(self, url, header=None, retry_time=3, retry_interval=5, timeout=5, proxies=None, *args, **kwargs):
        if header:
            header.update({
                'User-Agent': str(self.user_agent(self)),
            })
        # print(url)
        # print(headers)
        # print(proxies)
        # while True:
        # try:
        proxies = {
            'http': 'http://120.77.46.4:6666',
            'https': 'http://120.77.46.4:6666'
        }
        url = header['TARGETURL']
        self.response = requests.get(url, headers=header, proxies=proxies, timeout=timeout, *args, **kwargs)
        return self
        # except Exception as e:
        #     retry_time -= 1
        #     if retry_time <= 0:
        #         resp = Response()
        #         resp.status_code = 200
        #         return self
        #     time.sleep(retry_interval)

    def easyGet(self, url, header=None, timeout=5, proxies=None, *args, **kwargs):
        if not url:
            return
        # print(url)
        # print(header)

        proxies = {
            'http': 'http://120.77.46.4:6666',
            'https': 'http://120.77.46.4:6666'
        }
        url = header['TARGETURL']

        if 'amazon' in url:
            requests.packages.urllib3.disable_warnings()
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
            try:
                print(proxies)
                requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += ':HIGH:!DH:!aNULL'
            except AttributeError:
                # no pyopenssl support used / needed / available
                pass
        try:
            self.response = requests.get(url, headers=header, proxies=proxies, timeout=timeout, *args, **kwargs)
            return self
        except Exception as e:
            print(e)
            logService().info(msg='采集错误，url = ' + url + 'proxies = ' + str(proxies), fileName=self.__class__.__name__)
            return False

    def easyAmazonGet(self, url, header=None, timeout=5, proxies=None, *args, **kwargs):
        if not url:
            return
        headers = self.header
        proxies = {
            'http': 'http://120.77.46.4:6666',
            'https': 'http://120.77.46.4:6666'
        }
        url = header['TARGETURL']
        if header and isinstance(header, dict):
            headers.update({
                'User-Agent': self.user_agent(self),
            })
        print(url)
        print(header)
        print(proxies)
        try:
            self.response = requests.get(url, headers=header, proxies=proxies, timeout=timeout, *args, **kwargs)
            return self
        except Exception as e:
            print(e)
            logService().info(msg='采集错误，url = ' + url + 'proxies = ' + str(proxies), fileName=self.__class__.__name__)
            return False


    def easyPost(self, url, headers=None, data=None, json=None, timeout=1, proxies=None, *args, **kwargs):
        i = 0
        while i < 3:
            try:
                self.response = requests.post(url=url, headers=headers, timeout=timeout, json=json)
                print(self.response)
                print(self.response.text)
                return self
            except Exception as e:
                i += 1
                print(e)


    def easyGetHead(self, url, header=None, timeout=5, proxies=None, *args, **kwargs):
        headers = self.header
        if header and isinstance(header, dict):
            headers.update(header)
        # print(url)
        # print(headers)
        # print(proxies)
        while True:
            try:
                self.response = requests.head(url, headers=headers, verify=False, proxies=proxies, timeout=timeout, *args, **kwargs)
                return self
            except Exception as e:
                return self

    """
     # 返回树型结构
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def tree(self):
        return etree.HTML(self.response.content)

    """
     # 返回text
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def text(self):
        return self.response.text

    """
         # 返回response
         # @param self
         # @return string
         # @author     WenMing    736038880@qq.com
         # @createTime 2021年1月7日 16:26:06
        """
    def getResponse(self):
        return self.response

    """
     # 返回content
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def content(self):
        return self.response.content

    """
     # 返回content
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def statusCode(self):
        result = 400
        try:
            statusCode = self.response.status_code
            if statusCode:
                result = statusCode
            return result
        except Exception as e:
            result = 400
            pass
        return result

    """
     # 返回json
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def json(self):
        result = {}
        responseText = self.response.text
        if not responseText:
            return result
        try:
            jsonResponseText = json.loads(self.text(), encoding='utf-8')
        except Exception as e:
            return result

        if not jsonResponseText:
            return result
        return jsonResponseText
