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
import requests
from lxml import etree
import random
from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent

import time
import hashlib
import datetime

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


def get_sku_mapping(sourceHtml_dict):
    mapping = {}
    for i in sourceHtml_dict['skuModule']['productSKUPropertyList']:
        for j in i['skuPropertyValues']:
            if j['propertyValueDisplayName']:
                j_name = j['propertyValueDisplayName']
            else:
                j_name = j['propertyValueName']
            mapping.update({j['propertyValueId']: i['skuPropertyName'] + ':' + j_name})
    return mapping


def get_desc(url):
    resp = requests.get(url, timeout=5)


    return resp.text


class ccAliexpressCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Aliexpress'

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
     # 保存文件
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月16日 10:11:43
    """

    def saveHtmlResult(self, url):
        commonRedisClass = commonRedis()
        commonElasticSearchClass = commonElasticSearch()
        itemid = re.search('https:.*aliexpress.*/item/(\d+).html.*', url).group(1)
        md5str = itemid
        itemid_validity = commonRedisClass.zscoreValByKey('aliexpress_info', '{}'.format(md5str))
        now_time = time.time()
        if itemid_validity != None:
            print('有缓存')
            shijiancha = int(now_time - itemid_validity)
            if shijiancha >= defaultApp.aliexpress_life_time['info']:
                print('已过期')
            else:
                print('没过期')
                print('http://47.107.142.65:9200/aliexpress_info/_doc/{itemid}'.format(itemid=md5str))
                data = commonElasticSearchClass.getSourceByIndexKey(index='aliexpress_info', doc_type="_doc",id=md5str)
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                return
        header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1'
        }
        for useType in '0111222':
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            header['user-agent'] = userAgent().getPc()
            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,timeout=10)
                html = result.text(self=WebRequest)

                data = self.setResult(html, url)  # 洗完的结构
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                commonElasticSearchClass.insertDataByIndexKey(index='aliexpress_info', id=md5str, data=data)
                commonRedisClass.insertDataByIndexKey(redisKeyName='aliexpress_info', redisStr=md5str)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                return
            except Exception as e:
                print('Error:',e)

    """
     # 判断是否为真实连接
     # @param self
     # @param htmlText 抓取页面
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月20日 16:19:15
    """

    def isTrueHtml(self, htmlText, url):
        return True

    """
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """

    def setResult(self, sourceHtml, url):
        print(url)
        data = {
            'base': {
                "productId": "",
                "title": "",
                "brand": '',
                "sourceUrl": "",
                "site": "",
                "currency": "",
                "price": "",
                "priceRange": "",
                "siteLanguage": "",
                "business_years": 0,  # 商家年限
                "location": "",  # 地区
                "contact_seller": "",  # 联系卖家
                "goods_description": "",  # 货描
                "return_rate": "",  # 回头率
                "goods_deliver": "",  # 发货
                "response": "",  # 响应
                "management_model": "",  # 经营模式
                "supply_level": "",  # 供应等级
                "sales": "",  # 销量
                "collection_volume": "",  # 收藏量
                "praise_rate": "",  # 好评率
                "product_rating": "",  # 商品评分
                "comments_number": 0,  # 评论数量
                "quantity": 0,
                "mall_id": "",
                "mall_link": "",
                "mall_name": "",
                "size": "",
                "weight_value": '',  # 重量值
                "weight_unit": '',  # 重量单位
            },
            'extra_data': [],
            'images': [],
            'attributes': [],
            'variableList': [],
            'is_valid': '',
            'extra': '',
            'extension': {
                'descriptionText': "",
                'description': ""
            }
        }
        data['base']['sourceUrl'] = url
        html_script = r'<script>(.*?)</script>'
        all_script = re.findall(html_script, sourceHtml, re.S | re.M)
        sourceHtml_re = ''
        for script_i in all_script:
            if 'window.runParams' in script_i:
                # print(script_i)
                sourceHtml_re = re.search('window.runParams = {[\s\S]*data: ({[\s\S]*}}),',sourceHtml)
        if sourceHtml_re == None:
            return
        need_data = sourceHtml_re.group(1)

        sourceHtml_dict = json.loads(need_data)
        # get_sku_mapping(sourceHtml_dict)

        itemid = sourceHtml_dict['actionModule']['productId']
        data['base']['productId'] = itemid

        title = sourceHtml_dict['pageModule']['title']
        data['base']['title_en'] = title

        currency = sourceHtml_dict['priceModule']['minAmount']['currency']
        data['base']['currency'] = currency

        price = sourceHtml_dict['priceModule']['minAmount']['value']
        data['base']['price'] = price
        if 'ActivityAmount' in sourceHtml_dict['priceModule']:
            minprice = sourceHtml_dict['priceModule']['minActivityAmount']['value']
            maxprice = sourceHtml_dict['priceModule']['maxActivityAmount']['value']
        else:
            minprice = sourceHtml_dict['priceModule']['minAmount']['value']
            maxprice = sourceHtml_dict['priceModule']['maxAmount']['value']
        data['base']['priceRange'] = "{}~{}".format(minprice, maxprice)

        sales = sourceHtml_dict['titleModule']['formatTradeCount']
        data['base']['sales'] = sales

        product_rating = sourceHtml_dict['titleModule']['feedbackRating']['averageStar']
        data['base']['product_rating'] = product_rating

        comments_number = sourceHtml_dict['titleModule']['feedbackRating']['totalValidNum']  # 评论数量
        data['base']['comments_number'] = comments_number

        quantity = sourceHtml_dict['actionModule']['totalAvailQuantity']
        data['base']['quantity'] = quantity

        mall_id = sourceHtml_dict['storeModule']['storeNum']
        data['base']['mall_id'] = mall_id

        mall_link = 'https:' + sourceHtml_dict['storeModule']['storeURL']
        data['base']['mall_link'] = mall_link

        mall_name = sourceHtml_dict['storeModule']['storeName']
        data['base']['mall_name'] = mall_name

        praise_rate = sourceHtml_dict['storeModule']['positiveRate']
        data['base']['praise_rate'] = praise_rate

        collection_volume = sourceHtml_dict['storeModule']['followingNumber']
        data['base']['collection_volume'] = collection_volume

        weights = sourceHtml_dict['specsModule'].get('props')
        if weights:
            for item in weights:
                attrName = item.get('attrName')
                attrValue = item.get('attrValue')
                if 'Weight' in attrName:
                    if 'kg' in attrValue:
                        data['base']['weight_unit'] = 'kg'
                        data['base']['weight_value'] = str(attrValue).replace('kg','')
                    elif 'g' in attrValue:
                        data['base']['weight_unit'] = 'g'
                        data['base']['weight_value'] = str(attrValue).replace('g','')

            if 'size' in attrName:
                data['base']['size'] = attrValue

        info2 = []
        attributes = sourceHtml_dict['specsModule']['props']
        for i,attr_i in enumerate(attributes):
            data_i = {
                "productId": itemid + int(str(time.time()).replace('.','')[-3:]) + i,
                "pkey": attr_i['attrName'],
                "pval": attr_i['attrValue'],
                "unit": ""
            }
            info2.append(data_i)
        data['attributes'] = info2

        descriptionTextlist = []
        for attr_i in attributes:
            infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=attr_i['attrName'],
                                                                            value=attr_i['attrValue'])
            descriptionTextlist.append(infostr)
        descriptionText = ''.join(descriptionTextlist)
        data['extension']['descriptionText'] = descriptionText


        imglist2 = []
        for img_i in sourceHtml_dict['imageModule']['imagePathList']:
            img_i_data = {
                "type": 0,
                "imgUrl": str(img_i)
            }
            imglist2.append(img_i_data)
        desc_url = sourceHtml_dict['descriptionModule']['descriptionUrl']
        print(desc_url)
        desc = get_desc(desc_url)  # 描述图
        print(len(desc))
        if desc:
            data['extension']['description'] =descriptionText+ desc
            desc_HTML = etree.HTML(desc)
            des_imglist = desc_HTML.xpath('//img/@src')
            for img_i in des_imglist:
                img_i_data = {
                    "type": 1,
                    "imgUrl": str(img_i)
                }
                imglist2.append(img_i_data)

        data['images'] = imglist2

        variableList2 = []
        if 'productSKUPropertyList' in sourceHtml_dict['skuModule']:
            skuPropertyValues= sourceHtml_dict['skuModule']['productSKUPropertyList']
            propimgmap = {}
            for skuPropertyValues_i in skuPropertyValues:
                skuPropertyValues =skuPropertyValues_i['skuPropertyValues']
                for skuPropertyValues_i in skuPropertyValues:
                    kk = skuPropertyValues_i['propertyValueId']
                    try:
                        vv = skuPropertyValues_i['skuPropertyImagePath']
                        propimgmap.update({str(kk): str(vv)})
                    except KeyError:
                        pass


            sku_mapping = get_sku_mapping(sourceHtml_dict)

            for i,variable_data in enumerate(sourceHtml_dict['skuModule']['skuPriceList']):
                productId = int(str(itemid) + '{}'.format(i))
                base_i = {
                    "productId": productId,
                    "title": str(title),
                    "currency": variable_data['skuVal']['skuAmount']['currency'],
                    "price": variable_data['skuVal']['skuAmount']['value'],
                    "priceRange": "",
                    "stock": int(variable_data['skuVal']['availQuantity']),
                    "sales": 0
                }
                attributes_data = []

                for c,j in enumerate(variable_data['skuPropIds'].split(',')):
                    productId_c = int(str(productId) + '{}'.format(c))
                    if int(j) in sku_mapping:
                        attributes_i = {
                            "pkey": sku_mapping[int(j)].split(':')[0],
                            "productId": productId_c,
                            "pval": sku_mapping[int(j)].split(':')[1],
                            "unit": ""
                        }
                    else:
                        continue

                    attributes_data.append(attributes_i)

                images_i = []
                skuPropIdslist = variable_data['skuPropIds'].split(',')
                for skuPropId_i in skuPropIdslist:
                    try:
                        imgUrl = propimgmap[str(skuPropId_i)]
                        img_data = {
                            "type": "3",
                            "imgUrl": imgUrl
                        }
                        images_i.append(img_data)
                    except KeyError:
                        pass

                varia_i = {
                    "base": base_i,
                    "attributes": attributes_data,
                    "images": images_i
                }
                variableList2.append(varia_i)
            data['variableList'] = variableList2
        return data

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

    def replaceCharEntity(self, htmlstr):
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
