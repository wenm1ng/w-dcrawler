# coding: utf-8
import datetime
import hashlib
import random
import re, os, json, time

import elasticsearch
import redis
import requests
from Configs.defaultApp import rootDir
from hashlib import md5
from App.common.webRequest import WebRequest
from App.common.url.baseUrlHandle import baseUrlHandle
from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis
from Configs import defaultApp
from App.service.system.classContextService import classContextService
from App.service.system.logService import logService
import json, gevent
from App.common.funs import appendDict
import importlib

from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''

domain_list = {
    'th': 'shopee.co.th',
    'sg': 'shopee.sg',
    'id': 'shopee.co.id',
    'my': 'shopee.com.my',
    'vn': 'shopee.vn',
    'ph': 'shopee.ph',
    'tw': 'xiapi.xiapibuy.com',
    'br': 'shopee.com.br'
}


def get_sales(sale31_list):
    data = {
        "three_day_sold": -1,
        "seven_day_sold": -1,
        "fifteen_day_sold": -1,
        "thirty_day_sold": -1
    }
    if sale31_list == []:
        return data
    else:
        if len(sale31_list) >= 31:
            sales3 = sale31_list[-1] - sale31_list[-4]
            sales7 = sale31_list[-1] - sale31_list[-8]
            sales15 = sale31_list[-1] - sale31_list[-16]
            sales30 = sale31_list[-1] - sale31_list[-30]
            data.update({
                "three_day_sold": sales3,
                "seven_day_sold": sales7,
                "fifteen_day_sold": sales15,
                "thirty_day_sold": sales30
            })

        elif len(sale31_list) >= 16:
            sales3 = sale31_list[-1] - sale31_list[-4]
            sales7 = sale31_list[-1] - sale31_list[-8]
            sales15 = sale31_list[-1] - sale31_list[-16]
            data.update({
                "three_day_sold": sales3,
                "seven_day_sold": sales7,
                "fifteen_day_sold": sales15
            })

        elif len(sale31_list) >= 8:
            sales3 = sale31_list[-1] - sale31_list[-4]
            sales7 = sale31_list[-1] - sale31_list[-8]
            data.update({
                "three_day_sold": sales3,
                "seven_day_sold": sales7
            })

        elif len(sale31_list) >= 4:
            sales3 = sale31_list[-1] - sale31_list[-4]
            data.update({"three_day_sold": sales3})

        return data


def get_md5(str):
    strmd5 = hashlib.md5(str.encode(encoding='UTF-8')).hexdigest()
    return strmd5


def getcreg(categories):
    dataee = {}
    for i, j in enumerate(categories):
        dataee.update({i: j})
    return dataee


def setResult(sourceHtml, url, Shopee_country):
    print(url)
    data = {
        'extra_data': [],
        'base': {
            "productId": "",
            "title": "",
            "title_en": "",
            "brand": '',
            "sourceUrl": "",
            "site": "",
            "currency": "",
            "price": "",
            "priceRange": "",
            "siteLanguage": "en",
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
            "monthly_sales": "",  # 平台自有月销量
            "categories_bag": {},
            "sales_bag": {

            },
            "delivery_bag": {
                "Free_shipping": -1,
                "Shipping": -1
            },
            "estimated_days": -1,  # 发货天数
            "product_rating": -1,  # 商品评分
            "comments_number": -1,  # 评论数量
            "collection_volume": "",  # 收藏量
            "praise_rate": "",  # 好评率
            "quantity": "",
            "mall_id": "",
            "mall_link": "",
            "mall_name": ""
        },
        "image": '',
        'images': [],
        'attributes': [],
        'variableList': [],
        'is_valid': '',
        'extra': '',
        'extension': {
            'descriptionText': "",
            'description': ""
        },
        'sales31': [],
        "update_timestamp": int(time.time()),
        "update_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    }

    data['base']['sourceUrl'] = url

    sourceHtml_dict = json.loads(sourceHtml)

    itemid = sourceHtml_dict['item']['itemid']
    data['base']['productId'] = itemid

    shopid = sourceHtml_dict['item']['shopid']
    data['base']['mall_id'] = shopid

    title = sourceHtml_dict['item']['name']
    data['base']['title_en'] = title

    price = sourceHtml_dict['item']['price'] / 100000

    data['base']['price'] = price

    location = sourceHtml_dict['item']['shop_location']
    data['base']['location'] = location

    sales = sourceHtml_dict['item']['historical_sold']
    data['base']['sales'] = sales

    monthly_sales = sourceHtml_dict['item']['sold']
    data['base']['monthly_sales'] = monthly_sales

    categories = sourceHtml_dict['item']['categories']
    catidlist = [-1 if i['catid'] == None else i['catid'] for i in categories]
    categories_bag = getcreg(catidlist)
    data['base']['categories_bag'] = categories_bag

    product_rating = sourceHtml_dict['item']['item_rating']['rating_star']
    data['base']['product_rating'] = product_rating

    quantity = sourceHtml_dict['item']['stock']
    data['base']['quantity'] = quantity

    estimated_days = sourceHtml_dict['item']['estimated_days']
    data['base']['quantity'] = estimated_days

    comments_number = sourceHtml_dict['item']['item_rating']['rating_count'][0]
    data['base']['comments_number'] = comments_number

    site = Shopee_country.upper()
    data['base']['site'] = site

    currency = sourceHtml_dict['item']['currency']
    data['base']['currency'] = currency

    mall_id = sourceHtml_dict['item']['shopid']
    data['base']['mall_id'] = mall_id

    mall_link = 'https://{}/shop/{}/search'.format(domain_list[Shopee_country], mall_id)
    data['base']['mall_link'] = mall_link

    image = sourceHtml_dict['item']['image']
    data['image'] = image

    imglist2 = []
    for img_i in sourceHtml_dict['item']['images']:
        img_i_data = {
                         "type": 0,
                         "imgUrl": 'https://cf.shopee.co.th/file/' + str(img_i)
                     },
        imglist2.append(img_i_data[0])
    data['images'] = imglist2

    data['base']['currency'] = currency

    info2 = []
    attributes = sourceHtml_dict['item']['attributes']
    for attr_i in attributes:
        data_i = {
            "productId": itemid,
            "pkey": attr_i['name'],
            "pval": attr_i['value'],
            "unit": ""
        }
        info2.append(data_i)
    data['attributes'] = info2

    variableList2 = []

    sku_img_mapping2 = {}
    tier_var_name = sourceHtml_dict['item']['tier_variations']
    if tier_var_name == []:
        pass
    else:
        tier_var_name = sourceHtml_dict['item']['tier_variations'][0]['name']
        sku_img_name = sourceHtml_dict['item']['tier_variations'][0]['options']
        sku_img = sourceHtml_dict['item']['tier_variations'][0]['images']
        sku_img_mapping = tuple(zip(sku_img_name, sku_img))
        for i in sku_img_mapping:
            sku_img_mapping2.update({i[0]: i[1]})

    models = sourceHtml_dict['item']['models']
    for models_i in models:
        base_i = {
            "productId": models_i['modelid'],
            "title": models_i['name'],
            "currency": currency,
            "price": float(int(models_i['price']) / 100000),
            "priceRange": "",
            "stock": models_i['stock'],
            "sales": models_i['sold']
        }

        attributes_i = []
        attr_i = {
            "pkey": tier_var_name,
            "productId": str(itemid),
            "pval": models_i['name'],
            "unit": ""
        }
        attributes_i.append(attr_i)

        sku_imglist = []
        try:
            img = 'https://cf.shopee.co.th/file/' + sku_img_mapping2[models_i['name']]
            img_data = {
                "type": "3",
                "imgUrl": img
            }
            sku_imglist.append(img_data)
        except:
            pass

        varia_i = {
            "base": base_i,
            "attributes": attributes_i,
            "images": sku_imglist
        }
        variableList2.append(varia_i)
    data['variableList'] = variableList2

    descriptionTextlist = []
    for attr_i in attributes:
        infostr = '<li title="{value}">{key}:&nbsp;{value}</li>'.format(key=attr_i['name'], value=attr_i['value'])
        descriptionTextlist.append(infostr)
    descriptionText = '<ul>' + ''.join(descriptionTextlist) + '</ul>'
    data['extension']['descriptionText'] = descriptionText

    description = sourceHtml_dict['item']['description']
    data['extension']['description'] = descriptionText + description

    data['sales31'] = [sales]
    # print(json.dumps(data))
    return data
    # desc_req = self.session.get(desc_url, headers=self.desc_headers, timeout=10)
    # result = self.parse_description(desc_req, product_data)
    # result_json = json.dumps(result)
    # sentinelServMaster.lpush(self.item_key, result_json)


class relayService(object):
    """
    # 路由集合
    # @var dict
    """
    routerMap = {
        'urls': {
            'channelsPrefix': 'cc',
            'channelsFold': 'urlsChannels',
            'channelsTail': 'CrawlService',
        },
        'choiceProduct': {
            'channelsPrefix': 'cc',
            'channelsFold': 'choiceProduct',
            'channelsTail': 'CrawlService',
        },
    }

    """
     # 设置路由键值
     # @param self
     # @param urls  list 连接数组
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月30日 16:55:08
    """

    def setRouterMapKey(self, key):
        if not key:
            return
        classContextService().setVarByNameValue(name=self.__class__.__name__ + '_routerMapKey', value=key)

    """
     # 设置路由键值
     # @param self
     # @param urls  list 连接数组
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月30日 16:55:08
    """

    def setChannel(self, key):
        if not key:
            return
        classContextService().setVarByNameValue(name=self.__class__.__name__ + '_channel', value=key)

    """
     # 设置路由键值
     # @param self
     # @param urls  list 连接数组
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月30日 16:55:08
    """

    def setParamsType(self, key):
        if not key:
            return
        classContextService().setVarByNameValue(name=self.__class__.__name__ + '_paramsType', value=key)

    """
     # 设置第一步采集连接
     # @param self
     # @param urls  list 连接数组
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """

    def setDefaultUrlsChannelsAsynchrTask(self, jsonParams):
        redis_indexname_info = 'urlsChannels_info_default'
        commonRedis().redispush(flag=0, redisKeyName=redis_indexname_info, data=json.dumps(jsonParams))

    """
     # 设置第一步采集连接
     # @param self
     # @param urls  list 连接数组
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """

    def setUrlsType(self, urlsType):
        classContextService().setVarByNameValue(name=self.__class__.__name__ + '_UrlsType', value=urlsType)
        pass

    """
     # 设置第一步采集连接
     # @param self
     # @param urls  list 连接数组
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """

    def setUrls(self, urls):
        if not urls:
            return False

        completeFormatUrls = {}
        completeFormatOriginalUrls = {}
        for key, val in enumerate(urls):
            platform = 'Wa'
            appendDict(completeFormatUrls, platform, key, baseUrlHandle(val).getConciseUrl())
            appendDict(completeFormatOriginalUrls, platform, key, val)

        classContextService().setVarByNameValue(name=self.__class__.__name__ + '_urls', value=completeFormatUrls)
        classContextService().setVarByNameValue(name=self.__class__.__name__ + '_originalUrls',
                                                value=completeFormatOriginalUrls)

    """
     # 关键词选品
     # @param self
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年5月10日 19:25:32
    """

    def getOnlineChoicProductResult(self):
        result = {}
        jsonParams = classContextService().getVarByName(name='baseController_jsonParams')
        commonRedisClass = commonRedis()

        md5JsonParams = hashlib.md5(str(jsonParams).encode(encoding='UTF-8')).hexdigest()
        cacheList = commonRedisClass.getStringByKey(md5JsonParams)
        if cacheList:
            return json.loads(cacheList)

        channel = classContextService().getVarByName(name=self.__class__.__name__ + '_channel')
        paramsType = classContextService().getVarByName(name=self.__class__.__name__ + '_paramsType')
        routerMap = classContextService().getVarByName(name=self.__class__.__name__ + '_routerMapKey')

        if not routerMap:
            return result
        if routerMap not in self.routerMap:
            return result
        if not channel:
            channel = 'Common'
        if not paramsType:
            channel = 1
        routerMapDict = self.routerMap[routerMap]
        className = routerMapDict['channelsPrefix'] + channel + routerMapDict['channelsTail']
        moduleStr = 'App.service.crawl.' + routerMapDict['channelsFold'] + '.' + className
        print(moduleStr)
        importModule = importlib.import_module(moduleStr)
        importModuleClassStr = getattr(importModule, className)
        if importModuleClassStr:
            importModuleClass = importModuleClassStr()
            importModuleClass.setRelayServiceClass(relayServiceClass=self)

            if paramsType == '0':
                result = importModuleClass.getCategory()
            elif paramsType == '1':
                result = importModuleClass.getClouldList()
            elif paramsType == '2':
                result = importModuleClass.getLocalList()
            elif paramsType == '3':
                result = importModuleClass.getInfo()
            elif paramsType == '4':
                result = importModuleClass.getItemLoc()
            elif paramsType == '5':
                result = importModuleClass.getParentCategoryId()

        commonRedisClass.setStringByKey(md5JsonParams,value=json.dumps(result))
        return result

    """
     # 获取主页面请求
     # @param self
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月21日 14:08:56
    """

    def getResult(self):
        self.requestMainUrls()
        # self.requestMainUrls()
        # self.requestMainUrls()
        return True

    """
        # 主页面请求
        # @param self
        # @return bool
        # @author     WenMing    736038880@qq.com
        # @createTime 2021年1月21日 14:08:56
       """

    def requestMainUrls(self):
        urls = classContextService().getVarByName(name=self.__class__.__name__ + '_urls')
        routerMap = classContextService().getVarByName(name=self.__class__.__name__ + '_routerMapKey')
        print(urls)
        result = False
        if not urls:
            return result
        if not routerMap:
            return result
        if routerMap not in self.routerMap:
            return result
        routerMapDict = self.routerMap[routerMap]

        for urlsKey, urlsVal in enumerate(urls):
            className = routerMapDict['channelsPrefix'] + urlsVal + routerMapDict['channelsTail']
            print('className:', className)
            moduleStr = 'App.service.crawl.' + routerMapDict['channelsFold'] + '.' + className
            importModule = importlib.import_module(moduleStr)
            importModuleClassStr = getattr(importModule, className)
            if importModuleClassStr:
                importModuleClass = importModuleClassStr()
                importModuleClass.setRelayServiceClass(relayServiceClass=self)
                importModuleClass.appendCurlRequest()
                importModuleClass.resetClassVar()
        return True

    """
     # 执行任务
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:58:59
    """

    def execHttpTak(self):
        httpTask = classContextService().getVarByName(name=self.__class__.__name__ + '_httpTask')
        if not httpTask:
            return False
        gevent.joinall(httpTask)
        classContextService().resetListVarByName(name=self.__class__.__name__ + '_httpTask')

    """
     # 检验平台
     # @param self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月15日 17:55:58
    """

    def checkPlatform(self, url):
        return baseUrlHandle(url).getPlatformAndSite()['platform'].capitalize()

    """
     # 设置扩展
     # @param self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月15日 17:55:58
    """

    def setProductCenterExtInfo(self, info):
        classContextService().setVarByNameValue(name='relayService_productCenterExtInfo', value={
            'companyCode': info['companyCode'],
            'userId': info['userId'],
        })

    """
     # 获取扩展
     # @param self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月15日 17:55:58
    """

    def getProductCenterExtInfo(self):
        return classContextService().getVarByName(name='relayService_productCenterExtInfo')

    """
     # 获取扩展
     # @param self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月15日 17:55:58
    """

    def getJsonData(self):
        return classContextService().getVarByName(name=self.__class__.__name__ + '_jsonData')

    """
     # 重置
     # @param self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月15日 17:55:58
    """

    def resetClassVar(self):
        relayService.urls = []

    """
    # 判断是否是json字符串
    """

    def check_json_format(json_str):
        if isinstance(json_str, str):
            try:
                json.loads(json_str, encoding='utf-8')
            except ValueError:
                return False
            return True
        else:
            return False

    """
        # 删除当前成功采集连接
        # @param self
        # @param url   链接
        # @return void
        # @author     WenMing    736038880@qq.com
        # @createTime 2021年3月31日 15:48:46
       """

    def delUrlsCrawlerSuccessByUrl(self, url):
        if not url:
            return
        result = {}
        urls = classContextService().getVarByName(name=self.__class__.__name__ + '_originalUrls')
        print("task:", urls)
        for channels in urls:
            for channelsUrl in urls[channels]:
                if urls[channels][channelsUrl] != url:
                    if channels in result:
                        result[channels].update({channelsUrl: urls[channels][channelsUrl]})
                    else:
                        result.update({channels: {channelsUrl: urls[channels][channelsUrl]}})

        if result:
            classContextService().setVarByNameValue(name=self.__class__.__name__ + '_originalUrls', value=result)
        else:
            classContextService().resetVarByName(name=self.__class__.__name__ + '_originalUrls')

        return

    """
     # 发送连接采集成功的json数据
     # @param self
     # @param jsonResult
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:48:02
    """

    def postProductCenterLinkJsonResult(self, data):
        urlsType = classContextService().getVarByName(name=self.__class__.__name__ + '_UrlsType')
        # 默认类型，直接返回参数
        if urlsType == 1:
            classContextService().setVarByNameValue(name=self.__class__.__name__ + '_jsonData', value=data)
            return

        jsonResult = {
            'data': {
                'list': [
                    data
                ]
            }
        }
        post_url = str(defaultApp.productCenterUrl) + 'api/product/reptiles/v2'
        headers = {
            'content-type': 'application/json',
        }
        if isinstance(jsonResult, str):
            jsonResult = dict(json.loads(jsonResult))
        jsonResult['companyCode'] = self.getProductCenterExtInfo()['companyCode']
        jsonResult['userId'] = self.getProductCenterExtInfo()['userId']
        # print(post_url)
        # print(headers)
        print(json.dumps(jsonResult))
        try:
            WebRequest().easyPost(url=post_url, headers=headers, json=jsonResult)
        except Exception as e:
            print('发送产品中心错误，错误信息 = ' + str(e) + ' 链接=' + str(post_url) + 'json-result = ' + str(jsonResult))
            print(e)
            return False
        return True

    """
     # 发送连接采集成功的json数据
     # @param self
     # @param jsonResult
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:48:02
    """

    def getProductCenterInfo(self, data,type):
        sourceName = '淘宝'
        if type =='ShopeeInfo':
            sourceName = 'shopee'
        if type=='PddInfo':
            sourceName = '拼多多'

        dataFormat = {
            "attribute": {
                "key": "",
                "pci_id": "",
                "pcv_id": "",
                "unit": "",
                "val": ""
            },
            "pc_id": 0,
            "source": sourceName,
            "source_url": "",
            "product_id": 0,
            "title": "",
            "price": 0,
            "collection_price": 0,
            "product_code": "",
            "pp_sku": "",
            "currency": "",
            "description_text": "",
            "description": "",
            "images": [],
            "variation": [],
            "srouce_type": "",
            "srouce_platform": "",
            "title_en": "",
            "retail_price": "",
            "stock": 0,
            "sales": 0,
            "brand": "",
            "weight": "",
            "weight_unit": "",
            "size_length": "",
            "size_width": "",
            "size_height": "",
            "size_unit": "",
            "desc_images": [
            ],
            "bullet_point": [
            ]
        }
        if not data:
            return dataFormat

        if data['attributes']:
            dataFormat['attribute']['key'] = data['attributes'][0]['pkey']
            dataFormat['attribute']['val'] = data['attributes'][0]['pval']
            dataFormat['attribute']['unit'] = data['attributes'][0]['unit']


        if 'productId' in data['base']:
            dataFormat['pc_id'] = data['base']['productId']
        if 'sourceUrl' in data['base']:
            dataFormat['source_url'] = data['base']['sourceUrl']
        if 'productId' in data['base']:
            dataFormat['product_id'] = data['base']['productId']
        if 'title' in data['base']:
            dataFormat['title'] = data['base']['title']
        if 'title_en' in data['base']:
            dataFormat['title_en'] = data['base']['title_en']
        if 'price' in data['base']:
            dataFormat['price'] = data['base']['price']
        if 'currency' in data['base']:
            dataFormat['currency'] = data['base']['currency']
        if 'sales' in data['base']:
            dataFormat['sales'] = data['base']['sales']
        if 'brand' in data['base']:
            dataFormat['brand'] = data['base']['brand']
        if 'site' in data['base']:
            dataFormat['srouce_platform'] = data['base']['site']

        if 'descriptionText' in data['extension']:
            dr = re.compile(r'<[^>]+>|:&nbsp;', re.S)
            dataFormat['description_text'] =  dr.sub('\n', str(data['extension']['descriptionText']))
        if 'description' in data['extension']:
            dataFormat['description'] = data['extension']['description']

        if 'images' in data:
            if data['images']:
                imagesTips = False
                for v_data in data['images']:
                    image = {
                        "pc_id": "",
                        "pcv_id": "",
                        "type": 0,
                        "il_id": "",
                        "img_url": "",
                        "oss_domain": "",
                        "oss_uri": ""
                    }
                    if not imagesTips:
                       image['type'] = 0
                    else:
                       image['type'] = 2
                    image['img_url'] = v_data['imgUrl']
                    dataFormat['images'].append(image)
                    imagesTips = True


        if 'variableList' in data:
            if data['variableList']:
                for variableInfo in data['variableList']:
                    variable = {
                        "pcv_id": 0,
                        "title": "",
                        "currency": "",
                        "attribute": {},
                        "collection_price": 0,
                        "stock": 0,
                        "sales": 0,
                        "weight": '',
                        "weight_unit": '',
                        "size_length": '',
                        "size_width": '',
                        "size_height": '',
                        "size_unit": '',
                        "url": "",
                        "variation_key1": "",
                        "variation_val1": "",
                        "variation_key2": "",
                        "variation_val2": "",
                        "variation_key3": "",
                        "variation_val3": "",
                    }

                    if variableInfo['attributes']:
                        lenAttributes = len(variableInfo['attributes'])
                        if lenAttributes >= 1:
                            variable['attribute']['key'] = variableInfo['attributes'][0]['pkey']
                            variable['attribute']['val'] = variableInfo['attributes'][0]['pval']
                            variable['attribute']['unit'] = variableInfo['attributes'][0]['unit']
                            variable['variation_key1'] = variableInfo['attributes'][0]['pkey']
                            variable['variation_val1'] = variableInfo['attributes'][0]['pval']
                        if lenAttributes >= 2:
                            variable['variation_key2'] = variableInfo['attributes'][1]['pkey']
                            variable['variation_val2'] = variableInfo['attributes'][1]['pval']
                        if lenAttributes >= 3:
                            variable['variation_key3'] = variableInfo['attributes'][2]['pkey']
                            variable['variation_val3'] = variableInfo['attributes'][2]['pval']

                    if 'images' in variableInfo:
                        if variableInfo['images']:
                            if 'imgUrl' in variableInfo['images'][0]:
                                variable['url'] = variableInfo['images'][0]['imgUrl']
                    variable['pcv_id'] = variableInfo['base']['productId']
                    variable['collection_price'] = variableInfo['base']['price']
                    variable['title'] = variableInfo['base']['title']
                    variable['currency'] = variableInfo['base']['currency']
                    variable['stock'] = variableInfo['base']['stock']
                    variable['sales'] = variableInfo['base']['sales']
                    dataFormat['variation'].append(variable)
        return dataFormat