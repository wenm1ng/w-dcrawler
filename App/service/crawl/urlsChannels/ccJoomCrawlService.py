# coding: utf-8

import re, os.path, time, urllib.parse

from App.common.webRequest import WebRequest
from Configs import defaultApp
from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis
from App.service.system.logService import logService
from App.model.crawl.channels.cc1688CrawlRedis import cc1688CrawlRedis
from scrapy.selector import Selector
from App.common.url.baseUrlHandle import baseUrlHandle
import json, gevent
from App.service.system.classContextService import classContextService
from lxml import etree

from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent

import hashlib
import datetime

from App.common.model.baseRedis import baseRedis

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


def get_detillimg(html):
    HTML = etree.HTML(html)
    des_imglist = HTML.xpath("/html/body/p//img/@src")
    return des_imglist


class ccJoomCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Joom'

    """
     # 设置对象
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:56:10
    """

    def setRelayServiceClass(self, relayServiceClass):
        if not relayServiceClass:
            return False
        if not self.relayServiceClass:
            self.relayServiceClass = relayServiceClass

    """
     # 获取数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:58:59
    """

    def appendCurlRequest(self):
        urls = classContextService().getVarByName(name=self.relayServiceClass.__class__.__name__ + '_originalUrls')
        if urls:
            if self.channleName not in urls.keys():
                return
            for url in urls[self.channleName]:
                if url not in urls[self.channleName]:
                    continue
                self.saveHtmlResult(urls[self.channleName][url])

    """
     # 获取数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:58:59
    """

    def appendExtendCurlRequest(self):
        return

    """
     # 保存文件
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月16日 10:11:43
    """

    def saveHtmlResult(self, url):
        commonRedisClass = commonRedis()
        commonElasticSearchClass = commonElasticSearch()
        itemid = re.search('https://www.joom.com/.*/products/(.*)?',url).group(1)
        # md5str = hashlib.md5(itemid.encode(encoding='UTF-8')).hexdigest()
        md5str = itemid
        itemid_validity = commonRedisClass.zscoreValByKey('joom_info', '{}'.format(md5str))
        now_time = time.time()
        if itemid_validity != None:
            print('有缓存')
            shijiancha = int(now_time - itemid_validity)
            if shijiancha >= defaultApp.soukuan_life_time['info']:
                print('已过期')
            else:
                print('没过期')
                print('http://47.107.142.65:9200/joom_info/_doc/{itemid}'.format(itemid=md5str))
                result = commonElasticSearchClass.getSourceByIndexKey(index='joom_info', doc_type="_doc", id=md5str)
                self.relayServiceClass.postProductCenterLinkJsonResult(jsonResult=result)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                return
        company_info = self.relayServiceClass.getProductCenterExtInfo()
        print(itemid)
        baseRedis.connectRedis(self).lpush('joom_url_task', url)
        baseRedis.connectRedis(self).set(itemid, json.dumps(company_info))
        baseRedis.connectRedis(self).expire(itemid, 500)
        self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
        return


    """
     # 判断是否为真实连接
     # @param self
     # @param htmlText 抓取页面
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月20日 16:19:15
    """

    def isTrueHtml(self, htmlText, url):
        print(url)
        result = False
        if not htmlText:
            return result
        resultTextSelector = etree.HTML(htmlText)
        if not resultTextSelector:
            return result
        productTitle = resultTextSelector.xpath('/html/head/title/text()')[0]
        print(productTitle)
        if productTitle:
            return True

    """
     # 当前url的数据保存至文件
     # @param self
     # @return string
     # @author     foolminx    foolminx@163.com
     # @date    2020-01-21 14:43:25
    """

    def setUrlsResult(self, url, company_code, user_id):
        return

    """
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """

    def setResult(self, sourceHtml, url):
        print(url)
        html = etree.HTML(sourceHtml)
        title = html.xpath("//h1[@class='detail-title']/text()")[0].replace('\n', '').replace('\r', '').replace(' ', '')
        sales = html.xpath("//ul[@class='detail-amount']/li[1]/text()")[0].replace('销量：', '')
        collection_volume = html.xpath("//ul[@class='detail-amount']/li[2]/text()")[0]
        collection_volume = re.search('.*(\d+)', collection_volume).group(1)
        info = html.xpath('//*[@id="main-con"]/div/div[2]/div[2]/div/div[1]/div[1]/ul/li/@title')  # 一些列表属
        imglist = html.xpath('//*[@class="tb-thumb owl-carousel owl-theme owl-loaded "]//a/img/@src')
        mallName = html.xpath("//h2[@class='shop-title']/text()")[0].replace('\n', '').replace('\r', '').replace(' ', '')
        descTemplate_script = '<script type="text/x-handlebars-template" id="descTemplate">(.*?)</script>'
        descdata = re.findall(descTemplate_script, sourceHtml, re.S | re.M)[0]

        html_script = r'<script>(.*?)</script>'
        script_info = re.findall(html_script, sourceHtml, re.S | re.M)  # 正则拿出所有<script>
        # print(script_info)
        # for i,j in enumerate (script_info):
        #     print(i,j)
        shop_script_info = script_info[-2]
        # print(json.dumps(shop_script_info))
        mallId = re.search("_SHOPID = '(\d+)';", shop_script_info).group(1)
        mallLink = 'https://www.vvic.com/shop/{}'.format(mallId)
        item_script_info = script_info[3]
        itemid = re.search("_ITEMID = '(\d+)';", item_script_info).group(1)
        price = re.search("_DISCOUNTPRICE = '(.*?)';", item_script_info).group(1)
        skuinfo = re.search("_SKUMAP = '(.*?)';", item_script_info).group(1)

        imglist2 = []
        for img_i in imglist:
            img_i_data = {
                             "type": 0,
                             "imgUrl": img_i if 'https:' in img_i else 'https:' + str(img_i)
                         },
            imglist2.append(img_i_data[0])
        des_imglist = get_detillimg(descdata)  # 描述图
        for img_i in des_imglist:
            img_i_data = {
                "type": 1,
                "imgUrl": str(img_i).replace('\\', '')
            }
            imglist2.append(img_i_data)

        info2 = []
        for attr_data in info:
            attr_data_i = attr_data.split(':')
            data_i = {
                "productId": str(itemid),
                "pkey": attr_data_i[0],
                "pval": attr_data_i[1],
                "unit": ""
            }
            info2.append(data_i)

        variableList2 = []
        for variable_data in json.loads(skuinfo):
            base_i = {
                "productId": int(itemid),
                "title": str(title),
                "currency": "CNY",
                "price": float(price),
                "priceRange": "",
                "stock": 0,
                "sales": 0
            }
            attributes_i = [
                {
                    "pkey": "颜色",
                    "productId": int(itemid),
                    "pval": variable_data['color_name'],
                    "unit": ""
                },
                {
                    "pkey": "规格",
                    "productId": int(itemid),
                    "pval": variable_data['size_name'],
                    "unit": ""
                }]

            images_i = []

            varia_i = {
                "base": base_i,
                "attributes": attributes_i,
                "images": images_i
            }
            variableList2.append(varia_i)

        description = {

            'description': descdata
        }

        product_data = {
            'data': {
                'list': [
                    {
                        'extra_data': [],
                        'base': {
                            "productId": str(itemid),
                            "title": str(title),
                            "brand": '',
                            "sourceUrl": str(url),
                            "site": "vvic",
                            "currency": "CNY",
                            "price": float(price),
                            "priceRange": "",
                            "siteLanguage": "zh",
                            "business_years": 0,  # 商家年限
                            "location": "",  # 地区
                            "contact_seller": "",  # 联系卖家
                            "goods_description": "",  # 货描
                            "return_rate": "",  # 回头率
                            "goods_deliver": "",  # 发货
                            "response": "",  # 响应
                            "management_model": "",  # 经营模式
                            "supply_level": "",  # 供应等级
                            "sales": int(sales),  # 销量
                            "collection_volume": int(collection_volume),  # 收藏量
                            "praise_rate": "",  # 好评率
                            "product_rating": "",  # 商品评分
                            "comments_number": 0,  # 评论数量
                            "quantity": 0,
                            "mall_id": str(mallId),
                            "mall_link": mallLink,
                            "mall_name": mallName
                        },
                        'images': imglist2,
                        'attributes': info2,
                        'variableList': variableList2,
                        'is_valid': '',
                        'extra': '',
                        'extension': description
                    }
                ]
            }
        }
        return product_data
        # desc_req = self.session.get(desc_url, headers=self.desc_headers, timeout=10)
        # result = self.parse_description(desc_req, product_data)
        # result_json = json.dumps(result)
        # sentinelServMaster.lpush(self.item_key, result_json)

    def judgeCommodityTrend(self, goodsDescript):
        '''
        判断商品描述是上升趋势还是下降趋势：trend = rise 上升， =decline 下降
        '''
        if not goodsDescript:
            return ''
        if 'Smaller' in goodsDescript:
            trend = 'decline'
        elif 'Higher' in goodsDescript:
            trend = 'rise'
        else:
            trend = ''
        return trend

    def resetClassVar(self):
        self.proxyIpPortList = []

    def entity(self, productId, product_title, currency, price, priceRange, infos, main_image, quantity, saleNums):
        data = {
            "base": {
                "productId": productId,
                "title": product_title,
                "currency": currency,
                "price": price,
                "priceRange": priceRange,
                "stock": quantity,
                "sales": saleNums
            },

            "attributes": infos,
            "images": [
                {
                    "type": 0,
                    "imgUrl": main_image,
                },
            ],
        }
        return data

    """
             # 去除html中的各种标签，保留文字数据
             # @param htmlstr html字符串
             # @return string
             # @author hongxuanqi
        """

    def filter_tags(self, htmlstr):
        # 先过滤CDATA
        re_cdata = re.compile('//<!\[CDATA\[[^>]*//\]\]>', re.I)  # 匹配CDATA
        re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I)  # Script
        re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I)  # style
        re_br = re.compile('<br\s*?/?>')  # 处理换行
        re_h = re.compile('</?\w+[^>]*>')  # HTML标签
        re_comment = re.compile('<!--[^>]*-->')  # HTML注释
        s = re_cdata.sub('', htmlstr)  # 去掉CDATA
        s = re_script.sub('', s)  # 去掉SCRIPT
        s = re_style.sub('', s)  # 去掉style
        s = re_br.sub('\n', s)  # 将br转换为换行
        s = re_h.sub('', s)  # 去掉HTML 标签
        s = re_comment.sub('', s)  # 去掉HTML注释
        # 去掉多余的空行
        blank_line = re.compile('\n+')
        s = blank_line.sub('\n', s)
        s = self.replaceCharEntity(s)  # 替换实体
        # 去除连续的空格和换行，将连续的换行替换成一个换行
        s = re.sub(' {2,}', '', s)
        s = re.sub('( \n)', '', s)
        s = re.sub('\n{2,}', '\n', s).strip()

        return s

    def replaceCharEntity(self,htmlstr):
        CHAR_ENTITIES = {'nbsp': ' ', '160': ' ',
                         'lt': '<', '60': '<',
                         'gt': '>', '62': '>',
                         'amp': '&', '38': '&',
                         'quot': '"', '34': '"', }

        re_charEntity = re.compile(r'&#?(?P<name>\w+);')
        sz = re_charEntity.search(htmlstr)
        while sz:
            entity = sz.group()  # entity全称，如&gt;
            key = sz.group('name')  # 去除&;后entity,如&gt;为gt
            try:
                htmlstr = re_charEntity.sub(CHAR_ENTITIES[key], htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
            except KeyError:
                # 以空串代替
                htmlstr = re_charEntity.sub('', htmlstr, 1)
                sz = re_charEntity.search(htmlstr)
        return htmlstr

    pass
