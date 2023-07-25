# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time      :   2022/5/10 15:33
# @Author    :   WenMing
# @Desc      :   
# @Contact   :   736038880@qq.com

import copy
import re, os.path, time, urllib.parse

import sys
import io

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
import elasticsearch
from App.common.ossUpload import ossUpload
from App.common.MysqlPool import MysqlPool
import random
from App.common import Config
from App.common.Exception import msgException

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


def get_md5(str):
    strmd5 = hashlib.md5(str.encode(encoding='UTF-8')).hexdigest()
    return strmd5


def getcreg(categories):
    dataee = {}
    for i, j in enumerate(categories):
        dataee.update({i: j})
    return dataee


class ccWaCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Wa'

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
        # commonRedisClass = commonRedis()
        # commonElasticSearchClass = commonElasticSearch()
        # if 'product' in url:
        #     re_url = re.search('https://.*?/product/(\d+)/(\d+)', url)
        # else:
        #     re_url = re.search('https://.*?-i.(\d+).(\d+)', url)
        # site = baseUrlHandle(url).getPlatformAndSite()['site']
        # netloc = baseUrlHandle(url).getPlatformAndSite()['netloc']
        # res = baseUrlHandle(url).getWaModule()
        # module = res['module']
        # category = res['category']

        # md5str = '{}_{}'.format(itemid, shopid)
        # itemid_validity = commonRedisClass.zscoreValByKey('shopee_info_{}'.format(site), '{}'.format(md5str))
        now_time = time.time()
        # if itemid_validity != None:
        #     print('有缓存')
        #     shijiancha = int(now_time - itemid_validity)
        #     if shijiancha >= defaultApp.shopee_life_time['info']:
        #         print('已过期')
        #     else:
        #         print('没过期')
        #         print('http://47.107.142.65:9200/shopee_info_{site}/_doc/{itemid}'.format(site=site, itemid=md5str))
        #         data = commonElasticSearchClass.getSourceByIndexKey(index='shopee_info_{}'.format(site),
        #                                                             doc_type="_doc", id=md5str, elasticsearchType=1)
        #         self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
        #         self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
        #         return

        header = {}
        print(777777777777777777777)
        print(url)
        # shopeurl = "https://{}/api/v2/item/get?itemid={}&shopid={}"
        for useType in '0':
            # needmd5 = "55b03-" + get_md5('55b03' + get_md5('itemid={}&shopid={}'.format(itemid, shopid)) + "55b03")
            # header['if-none-match-'] = needmd5
            # header['referer'] = 'https://{}/a-i.{}.{}'.format(netloc, shopid, itemid)
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            header['User-Agent'] = userAgent().getPc()
            rs = re.match(r'.*?expansion:(.*?) type.*?tag:(.*?)&.*?', url)
            if not rs.group(1) or not rs.group(2):
                raise Exception('采集链接错误')
            version = rs.group(1) #版本信息
            module = rs.group(2) #模块信息
            # 取数据类型
            if version not in Config.wow_version.keys():
                raise Exception('版本信息错误')
            version = Config.wow_version[version]

            occupation = ''
            tabTitle = ''
            tabType = 1

            if module in Config.wow_occupation.keys():
                # 某个职业的专页
                occupation = Config.wow_occupation[module]
            elif module in Config.wow_tab.keys():
                tabTitle = Config.wow_tab[module]['name']
                tabType = Config.wow_tab[module]['type']

            if not (occupation or (tabTitle and tabType)):
                raise Exception('tab信息错误')

            ttId = 0
            if tabTitle:
                # 查询是否已有tab数据
                where = {'=': {'type': tabType, 'title': tabTitle}}
                info = MysqlPool().first('wow_wa_tab_title', where)
                if not info:
                    # 添加到tab_title表
                    insertData = {
                        'version': version,
                        'type': tabType,
                        'title': tabTitle
                    }
                    field = ['version', 'type', 'title']
                    ttId = MysqlPool().batch_insert('wow_wa_tab_title', field, insertData)

            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                            timeout=5)
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
                # resStr = result.content(self=WebRequest).decode('utf-8')
                resArr = json.loads(result.content(self=WebRequest))
                time.sleep(max(0.3, round(random.random(), 2)))
                for val in resArr['hits']:
                    # 爬取wa详情页面信息
                    header['TARGETURL'] = 'https://data6.wago.io/lookup/wago?id='+val['id']
                    header['User-Agent'] = userAgent().getPc()

                    result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                                timeout=5)
                    resArr = json.loads(result.content(self=WebRequest))
                    # Config.wow_talent.keys()
                    talentName = ''
                    for v in resArr['categories']:
                        if module+'-' in v:
                            talentName = Config.wow_talent[v]

                    insertData = {
                        'version': version,
                        'occupation': occupation,
                        'talent_name': talentName,
                        'type': tabType,
                        'data_from': 2,
                        'tt_id': ttId,
                        'origin_url': resArr['url'],
                        'origin_title': resArr['name'],
                        'origin_description': resArr['description']['text']
                    }
                    # 爬取wa字符串信息
                    header['TARGETURL'] = 'https://data5.wago.io'+resArr['codeURL']
                    header['User-Agent'] = userAgent().getPc()
                    result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                                timeout=5)
                    resInfoArr = json.loads(result.content(self=WebRequest))
                    insertData['wa_content'] = resInfoArr['encoded']
                    waData = [insertData]
                    field = ['version', 'occupation', 'talent_name', 'type', 'data_from', 'tt_id', 'origin_url', 'origin_title', 'origin_description', 'wa_content']
                    waId = MysqlPool().batch_insert('wow_wa_content', field, waData)
                    print(insertData)

                    imageData = []
                    try:
                        for image in resArr['screens']:
                            if image['src']:
                                # tempData = {'image_url': ossUpload().uploadImageQiNiu(image['src']), 'wa_id': waId}
                                tempData = {'origin_image_url': image['src'], 'wa_id': waId}
                                imageData.append(tempData)
                    except Exception as es:
                        print('error file:' + es.__traceback__.tb_frame.f_globals["__file__"] + '_line:' + str(
                            es.__traceback__.tb_lineno) + '_msg:' + str(es))  # 发生异常所在的文件

                    if imageData:
                        field = ['origin_image_url', 'wa_id']
                        MysqlPool().batch_insert('wow_wa_image', field, imageData)
                    time.sleep(max(0.3, round(random.random(), 2)))
                    print('成功采集id:'+val['id'])
                # startPos = resStr.find("'{")
                # endPos = resStr.find("'}")
                # jsonStr = resStr[startPos:endPos]
                print(8888888888888888888888888)
                # data = self.setResult(result.content(self=WebRequest), url)  # 洗完的结构
                # print(666, data)
                return
            except Exception as e:
                print('error file:'+e.__traceback__.tb_frame.f_globals["__file__"]+'_line:'+str(e.__traceback__.tb_lineno)+'_msg:'+str(e))  # 发生异常所在的文件
                raise AssertionError(e)

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
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """

    def setResult(self, sourceHtml, url):

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
                    "three_day_sold": -1,
                    "seven_day_sold": -1,
                    "fifteen_day_sold": -1,
                    "thirty_day_sold": -1
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
                "mall_name": "",

                "front_desk_type": "",  # 前台分类
                "size": '',  # 尺寸
                "weight_value": '',  # 重量值
                "weight_unit": '',  # 重量单位
                "size_table": ''  # 尺码表
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

        if 'price_min' in sourceHtml_dict['item'] and 'price_max' in sourceHtml_dict['item']:
            priceRange = str(sourceHtml_dict['item']['price_min'] / 100000) + '~' +  str(sourceHtml_dict['item']['price_max'] / 100000)
            data['base']['priceRange'] = priceRange

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
        data['base']['product_rating'] = str(product_rating)[:3]

        quantity = sourceHtml_dict['item']['stock']
        data['base']['quantity'] = quantity

        estimated_days = sourceHtml_dict['item']['estimated_days']
        data['base']['quantity'] = estimated_days

        comments_number = sourceHtml_dict['item']['item_rating']['rating_count'][0]
        data['base']['comments_number'] = comments_number

        site = baseUrlHandle(url).getPlatformAndSite()['site'].upper()
        data['base']['site'] = site

        currency = sourceHtml_dict['item']['currency']
        data['base']['currency'] = currency

        mall_id = sourceHtml_dict['item']['shopid']
        data['base']['mall_id'] = mall_id
        dom = baseUrlHandle(url).getPlatformAndSite()['netloc']

        mall_link = 'https://{}/shop/{}/search'.format(dom, mall_id)
        data['base']['mall_link'] = mall_link

        image = sourceHtml_dict['item']['image']
        data['image'] = 'https://cf.{}/file/{}'.format(dom, str(image))
        if sourceHtml_dict['item']['currency'] == 'TWD':
            data['image'] = "https://s-cf-tw.shopeesz.com/file/{}".format(str(image))
        imglist2 = []
        for img_i in sourceHtml_dict['item']['images']:
            img_i_data = {
                "type": 0,
                "imgUrl": 'https://cf.{}/file/{}'.format(dom, str(img_i)) if sourceHtml_dict['item']['currency'] != 'TWD' else "https://s-cf-tw.shopeesz.com/file/{}".format(str(img_i))
            }
            if img_i_data:
                imglist2.append(img_i_data)

        data['images'] = imglist2

        data['base']['currency'] = currency

        # collection_volume
        data['base']['collection_volume'] = sourceHtml_dict['item']['liked_count']

        # front_desk_type
        front_desk_type_item = sourceHtml_dict['item']['categories']
        front_desk_type_list = []
        for item in front_desk_type_item:
            display_name = item['display_name']
            front_desk_type_list.append(display_name)
        data['base']['front_desk_type'] = '>'.join(front_desk_type_list)

        # "size_table": ''  # 尺码表
        size_tables = sourceHtml_dict['item'].get('size_chart')
        if size_tables:
            size_table = 'https://cf.shopee.com.my/file/' + size_tables
            data['base']['size_table'] = size_table


        info2 = []
        attributes = sourceHtml_dict['item']['attributes']
        for attr_i in attributes:
            data_i = {
                "productId": itemid,
                "pkey": attr_i['name'],
                "pval": attr_i['value'],
                "unit": ""
            }
            if 'Brand' in attr_i['name']:
                data['base']['brand'] = attr_i['value']

            info2.append(data_i)
        data['attributes'] = info2

        variableList2 = []

        sku_img_mapping2 = {}
        if sourceHtml_dict['item']['tier_variations']:
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
            infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=attr_i['name'], value=attr_i['value'])
            descriptionTextlist.append(infostr)
        descriptionText = ''.join(descriptionTextlist)
        data['extension']['descriptionText'] = descriptionText

        description = sourceHtml_dict['item']['description']
        data['extension']['description'] = descriptionText + description

        data['sales31'] = [sales]
        print(json.dumps(data))
        return data
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
