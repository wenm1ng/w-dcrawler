# -*- coding:utf-8 -*-
# @Time : 2021/1/13 9:47
# @Author: foolminx
# @File : urlHandle.py

from urllib.parse import urlparse
from Configs import site
from App.service.system.logService import logService
import re
from urllib.parse import urlparse


class baseUrlHandle(object):
    # 原始url
    url = ''

    scheme = ['http', 'https']

    platform = [
        'nil', 'amazon', 'ebay', 'aliexpress', '1688', 'bao66', 'jd', 'shopee', 'joom', 'taobao', 'tmall', 'wish', 'mobileyangkeduo'
    ]

    def __init__(self, url):
        if not url:
            return False
        self.setUrl(url)

    def parseUrl(self):
        if not self.url:
            return False
        parse = urlparse(self.url)

        return {
            'scheme': str(parse.scheme),
            'netloc': str(parse.netloc),
            'path': str(parse.path),
            'query': str(parse.query)
        }

    def setUrl(self, url):
        self.url = url

    def getUrl(self):
        return self.url

    def checkUrl(self):
        return 'true'

    def getConciseUrl(self):
        parse = self.parseUrl()
        if parse['scheme'] not in self.scheme:
            parse['scheme'] = self.scheme[1]
        # amazon单独处理
        platformSite = self.getPlatformAndSite()
        if platformSite['platform'] == 'amazon':
            amazonUrl = parse['path'].split('/')
            if amazonUrl[0] == '':
                del amazonUrl[0]
            if amazonUrl[0] == '-':
                del amazonUrl[0]
                del amazonUrl[0]
                amazonUrl.insert(0, '')
                parse['path'] = '/'.join(amazonUrl)
            amazonUrl = parse['path'].split('/')
            for au in amazonUrl:
                if re.search(re.compile(r'ref='), au):
                    amazonUrl.remove(au)
                parse['path'] = '/'.join(amazonUrl)
        if platformSite['platform'] == 'mobileyangkeduo':
            getGoodsId = ''
            queryResult = re.findall(r"\bgoods_id=\S+&\b", parse['query'])
            if queryResult:
                if queryResult[0]:
                    queryResult[0].strip('&')
                    getGoodsId = str(queryResult[0])
            else:
                getGoodsId = parse['query']
            parse['path'] += '?' + getGoodsId
        if platformSite['platform'] == 'taobao':
            getGoodsId = re.findall(r'id=(\d+)&?', parse['query'])
            if getGoodsId:
                if isinstance(getGoodsId, list):
                    parse['path'] += '?id=' + str(getGoodsId[0])
            else:
                parse['path'] = parse['query']
        if platformSite['platform'] == 'tmall':
            getGoodsId = re.findall(r'id=(\d+)&?', parse['query'])
            if getGoodsId:
                if isinstance(getGoodsId, list):
                    parse['path'] += '?id=' + str(getGoodsId[0])
            else:
                parse['path'] = parse['query']
        url = parse['scheme'] + '://' + parse['netloc'] + parse['path']
        return url

    #
    # 获取wa模块（pve pvp等）
    #
    def getWaModule(self):
        res = {
            'module': '',
            'category': ''
        }
        parse = self.parseUrl()
        # strip去除/ split = explode
        urlInfo = parse['path'].strip('/').split('/')
        res['module'] = urlInfo[1]
        res['category'] = urlInfo[2]
        print(res)
        return res
    #
    # 获取url的平台和站点
    # 默认平台小写，站点大写
    #
    def getPlatformAndSite(self):
        res = {
            'platform': '',
            'site': 'US',
            'platformType': 0,
        }
        parse = self.parseUrl()

        for pKey, pVal in site.site.items():
            for sKey, sVal in pVal.items():
                if parse['netloc'] == sKey:
                    res['site'] = str.upper(sVal)
                    res['platform'] = str.lower(pKey)
                    break

        if res['platform'] == '':
            if re.search(re.compile(r'amazon\.'), parse['netloc']):
                res['platform'] = 'amazon'
            elif re.search(re.compile(r'ebay\.'), parse['netloc']):
                res['platform'] = 'ebay'
            elif re.search(re.compile(r'aliexpress\.'), parse['netloc']):
                res['platform'] = 'aliexpress'
            elif re.search(re.compile(r'1688\.'), parse['netloc']):
                res['platform'] = '1688'
            elif re.search(re.compile(r'bao66\.'), parse['netloc']):
                res['platform'] = 'bao66'
            elif re.search(re.compile(r'jd\.'), parse['netloc']):
                res['platform'] = 'jd'
            elif re.search(re.compile(r'shopee\.'), parse['netloc']):
                res['platform'] = 'shopee'
            elif re.search(re.compile(r'joom\.'), parse['netloc']):
                res['platform'] = 'joom'
            elif re.search(re.compile(r'taobao\.'), parse['netloc']):
                res['platform'] = 'taobao'
            elif re.search(re.compile(r'tmall\.'), parse['netloc']):
                res['platform'] = 'tmall'
            elif re.search(re.compile(r'wish\.'), parse['netloc']):
                res['platform'] = 'wish'
            elif re.search(re.compile(r'yangkeduo\.'), parse['netloc']):
                res['platform'] = 'mobileyangkeduo'
            elif re.search(re.compile(r'pinduoduo\.'), parse['netloc']):
                res['platform'] = 'mobileyangkeduo'

            elif re.search(re.compile(r'lazada\.'), parse['netloc']):
                res['platform'] = 'lazada'

        # if parse['netloc'] == 'img.alicdn.com' or parse['netloc'] == 'itemcdn.tmall.com' or parse['netloc'] == 'desc.alicdn.com':
        #     res['platform'] = '1688'

        if res['platform'] == '':
            res['platform'] = '1688'

        # logService().info(msg='当前链接 = ' + str(e) + ' 链接=' + str(post_url) + 'json-result = ' + str(result), fileName=self.__class__.__name__)

        # 生成平台类型
        for i in range(0, len(self.platform)):
            if self.platform[i] == res['platform']:
                res['platformType'] = i

        if res['platform'] == 'shopee':
            netloc = parse['netloc'].split('.')
            res['netloc'] = parse['netloc']
            res['site'] = netloc[-1]
        if res['platform'] == 'lazada':
            netloc = parse['netloc'].split('.')
            res['netloc'] = parse['netloc']
            res['site'] = netloc[-1]
        print(res)
        return res


    pass
