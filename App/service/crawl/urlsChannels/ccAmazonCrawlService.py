# -*- coding: utf-8 -*-
from gevent import monkey

monkey.patch_all()
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

from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent

from concurrent.futures import ThreadPoolExecutor, as_completed
from lxml import etree
import hashlib
import datetime
import requests

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


# executor = ThreadPoolExecutor(10)

def filliter(infolist):
    infolist = [x.strip() for x in infolist if x.strip() != '']
    return infolist


def get_sku_img_mapping(Html):
    sku_img_mapping = {}

    img_a_k = Html.xpath('//div[@id="variation_color_name"]/ul/li/@title')
    img_a_v = Html.xpath('//div[@id="variation_color_name"]/ul/li//img/@src')

    img = tuple(zip(img_a_k, img_a_v))

    for i in img:
        k = str(i[0]).replace('选择 ', '')
        v = str(i[1])

        sku_img_mapping.update({k: v})
    return sku_img_mapping


def get_pricetext(data):
    pricetext = ""
    for i in data:
        if '"FeatureName" : "twister-slot-price_feature_div' in i:
            price = json.loads(i.replace(' ', ''))['Value']['content']['priceToSet']
            try:
                pricetext = price
            except:
                pricetext = ''
            break
    # print('pricetext:', pricetext)
    return pricetext


def get_stock(data):
    stock = ""
    for i in data:
        if '"FeatureName" : "desktop_buybox' in i:
            stock_html = json.loads(i.replace(' ', ''))['Value']['content']['desktop_buybox']
            html = etree.HTML(stock_html)
            try:
                stock = html.xpath('.//*[@id="quantity"]/option/@value')[-1]
            except:
                stock = ''

            break

    return stock


def get_info_html(data):
    info2_html = ""
    if data:
        for i in data:
            if '"FeatureName" : "productDescription_feature_div' in i:
                info2_html = '<h2>' + json.loads(i.replace('  ', ''))['Value']['content'][
                    'productDescription_feature_div'].replace('\n', '').replace('\r', '')

                break
    else:
        info2_html = ''
    return info2_html


def get_info2_html(data):
    info_html = ""
    if data:
        for i in data:
            if '"FeatureName" : "productDetails_feature_div' in i:
                info_html = json.loads(i.replace('  ', ''))['Value']['content'][
                    'productDetails_feature_div'].replace('\n', '').replace('\r', '')
                break
    else:
        info_html = ''
    return info_html


def get_description(html, site, itemid, parentAsin):
    # 黑標描述
    # Product Description 上
    # Product details     下

    # 黄標描述
    # Product description 上
    # Product information 下

    # NO.1
    desc1 = ''
    desc2 = ''
    detail_html = ''

    if desc1 == "":
        desc1_xpath = html.xpath('//div[@id="aplus3p_feature_div"]')
        if desc1_xpath:
            desc1 = etree.tostring(desc1_xpath[0]).decode()
            desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
            desc1 = desc1.replace('\n', '').replace('\r', '')
            # print(desc1)
            if len(desc1) < 500:
                desc1 = ""
        print(111)
    if desc1 == "":
        desc1_xpath = html.xpath('//div[@id="btf-content-1_feature_div"]')
        if desc1_xpath:
            desc1 = etree.tostring(desc1_xpath[0]).decode()
            desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
            desc1 = desc1.replace('\n', '').replace('\r', '')
            if len(desc1) < 500:
                desc1 = ""
        print(222)
    if desc1 == "":
        desc1_xpath = html.xpath('//div[@id="dp_productDescription_container_div"]')
        if desc1_xpath:
            desc1 = etree.tostring(desc1_xpath[0]).decode()
            desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
            desc1 = desc1.replace('\n', '').replace('\r', '')
            if len(desc1) < 500:
                desc1 = ""
        print(333)
    if desc1 == "":
        desc1_xpath = html.xpath('//div[@id="dpx-aplus-product-description_feature_div"]')
        if desc1_xpath:
            desc1 = etree.tostring(desc1_xpath[0]).decode()
            desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
            desc1 = desc1.replace('\n', '').replace('\r', '')
            if len(desc1) < 500:
                desc1 = ""
        print(444)
    if desc1 == "":
        desc1_xpath = html.xpath('//div[@id="btf-content-15-m_feature_div"]')
        if desc1_xpath:
            desc1 = etree.tostring(desc1_xpath[0]).decode()
            desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
            desc1 = desc1.replace('\n', '').replace('\r', '')
            if len(desc1) < 500:
                desc1 = ""
        print(555)
    if desc1 == "":
        desc1_xpath = html.xpath('//div[@id="btf-content-10_feature_div"]')
        if desc1_xpath:
            desc1 = etree.tostring(desc1_xpath[0]).decode()
            desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
            desc1 = desc1.replace('\n', '').replace('\r', '')
            if len(desc1) < 500:
                desc1 = ""
        print(666)
    if desc1 == "":
        desc1_xpath = html.xpath('//div[@id="dp_productDescription_container_div"]')
        if desc1_xpath:
            desc1 = etree.tostring(desc1_xpath[0]).decode()
            desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
            desc1 = desc1.replace('\n', '').replace('\r', '')

            if len(desc1) < 500:
                desc1 = ""
        print(888)

    if desc1 == "":
        desc1_xpath = html.xpath('//div[@id="dpx-aplus-brand-story_feature_div"]')
        if desc1_xpath:
            desc1 = etree.tostring(desc1_xpath[0]).decode()
            desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
            desc1 = desc1.replace('\n', '').replace('\r', '')
            if len(desc1) < 500:
                desc1 = ""
        print(999)
    if desc1 == "":
        desc = get_desc(site, itemid, parentAsin)
        desc1 = get_info_html(desc)
        print(777)

    if desc2 == "":
        htmlXpathdetailBullets = html.xpath('//div[@id="detailBullets"]')
        if htmlXpathdetailBullets:
            desc2 = etree.tostring(htmlXpathdetailBullets[0]).decode()
            desc2 = desc2.replace('\n', '').replace('\r', '')
    if desc2 == "":
        htmlXpathproduct_details_grid_feature_div = html.xpath('//div[@id="product-details-grid_feature_div"]')
        if htmlXpathproduct_details_grid_feature_div:
            desc2 = etree.tostring(htmlXpathproduct_details_grid_feature_div[0]).decode()
            desc2 = desc2.replace('\n', '').replace('\r', '')
    if desc2 == "":
        desc = get_desc(site, itemid, parentAsin)
        desc2 = get_info2_html(desc)
    description = desc1 + desc2
    # print(22222, description)

    return description, detail_html


def get_desc(site, sku, psku):
    domain = defaultApp.amz_domain_mapping[site]

    now_skuid = sku
    parentAsin = psku
    url = "{domain}/gp/page/refresh?acAsin={now_skuid}&asinList={now_skuid}&auiAjax=1&dcm=1&dpEnvironment=hardlines&dpxAjaxFlag=1&ee=2&enPre=1&id={now_skuid}&isFlushing=2&isUDPFlag=1&json=1&parentAsin={parentAsin}&pgid=pc_display_on_website&ptd=COMPUTER_DRIVE_OR_STORAGE&triggerEvent=Twister".format(
        domain=domain, now_skuid=now_skuid, parentAsin=parentAsin)
    header = {
        'accept': 'text/html,*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',

            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
    }
    for useType in '01112':
        print(url)
        header['USETYPE'] = useType
        header['TARGETURL'] = url
        header['User-Agent'] = userAgent().getPc()

        try:
            jsonResult = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                            timeout=5)
            resultText = jsonResult.text(self=WebRequest)
            if resultText:
                return resultText.replace('\n', '').replace('\r', '').split('&&&')

        except Exception as e:
            print('get_desc_error:', e)


class ccAmazonCrawlService(object):
    """
    # 对象
    # @var string
    """
    commonRedisClass = commonRedis()
    commonElasticSearchClass = commonElasticSearch()
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Amazon'

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
        # urls = classContextService().getVarByName(name=self.relayServiceClass.__class__.__name__ + '_urls')
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

    def post_small_data(self, site, data, ccode, uuid):

        now_skuid = data['base']['productId']
        parentAsin = data['base']['parent_identification']
        md5str = '{}_{}'.format(parentAsin, now_skuid)
        try:
            itemid_validity = self.commonRedisClass.zscoreValByKey('amazon_info_v_{}'.format(site), '{}'.format(md5str))
            now_time = time.time()
            # if itemid_validity != None:
            #     print('有缓存_v')
            #     shijiancha = int(now_time - itemid_validity)
            #     if shijiancha >= defaultApp.amazon_life_time['info']:
            #         print('已过期_v')
            #     else:
            #         print('没过期_v')
            #         print('http://47.107.142.65:9200/amazon_info_v/_doc/{itemid}'.format(itemid=md5str))
            #         result = self.commonElasticSearchClass.getSourceByIndexKey(index='amazon_info_v_{}'.format(site),
            #                                                                    doc_type="_doc",
            #                                                                    id=md5str)
            #         result = json.loads(result['datajson'])
            #         result['companyCode'] = ccode
            #         result['userId'] = uuid
            #         requests.post(defaultApp.productCenterUrl + 'api/product/crawler/large/variation',
            #                       data=json.dumps(result), timeout=2)
            #         flag = [True]
            #         return flag
            print('没缓存_v')
            desc_data = get_desc(site, now_skuid, parentAsin)
            pricetext = get_pricetext(desc_data)
            # print(666)

            if pricetext:
                pricetext = pricetext.replace(' ', '').replace(',', '.').replace('\xa0', '').split('-')[0]
                price = re.search('.*?(\d+\.\d+).*?', pricetext).group(1)
            else:
                price = ''
            stock = get_stock(desc_data)
            data['base']["price"] = str(price)
            data['base']["stock"] = str(stock)
            data2 = {

                "data": {"list": [{'variableList': [data]}]}
            }
            es_data = {
                'id': md5str,
                'datajson': json.dumps(data2),
                'type': 'amazon_info_v_{}'.format(site),
                'updated_time': str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            }
            self.commonElasticSearchClass.insertDataByIndexKey(index='amazon_info_v_{}'.format(site), id=md5str,
                                                               data=es_data)
            self.commonRedisClass.insertDataByIndexKey(redisKeyName='amazon_info_v_{}'.format(site), redisStr=md5str)

            data['companyCode'] = ccode
            data['userId'] = uuid
            requests.post(defaultApp.productCenterUrl + 'api/product/crawler/large/variation', data=json.dumps(data2),
                          timeout=2)

            flag = [True]
            # print('v+1:', json.dumps(data))
        except Exception as e:
            flag = [False, data, ccode, uuid]
            # print('v----------1:', e)
        return flag

    def saveHtmlResult(self, url):
        header = {
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br',
            # 'accept-language': 'zh-CN,zh;q=0.9',
            # 'cookie': 'session-id=144-4054991-2800846; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=134-6787062-1625066; session-token=3LM6xDx/5dnXDmH2OrPC/uzjhB6rWfdS1/GEKG5OH+z27WYX6Eq7KhW/MrYPKRq/kSDY0WuPKogk0KLMmh+X6sNecf627GUlgAQ9BketgogadRlEICMRoxx9Q0IQhoTpxdxqPtXY/Af/nMxcPGH5Dw5Jt2Jm7HIFO8jhMy+Qf+xTXK/mCCjqH886mjuDCiGs; csm-hit=tb:468826Z7M1PVP9Y5R5GT+s-TM8S0ZDG15SV0MZ6K818|1619078290003&t:1619078290003&adb:adblk_no; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:CN"; ubid-main=132-5043066-6035737; session-id=140-0976175-1923942; lc-main=zh_CN; session-token=gY5hmFq+U6it0pYJDfJqCquoi233F0h2bpOaRWxwlidPPqXwYvOTgPAEPXrh3RDefvjeEJCPTL0plYg8TkX/GgI8NfqPQj2iXLoHwChHZTeqZq38TrI6BTXhsu/PsJ3oPP5v7f/BiTXIWsyo9IMCdUE9TR6GUXZhkZoKl1fvy2xE7YrnGa4TdKOsyzfeopPO',
            # 'cache-control': 'max-age=0',
            # 'downlink': '10',
            # 'ect': '4g',
            # 'referer': 'https://www.amazon.com/-/szh/dp/B07KFZ77QD/ref=twister_B084YYBL7G?th=1',
            'rtt': '200',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            # 'auiAjax': '1',
            # 'dpEnvironment': 'softlines',
            # 'dpxAjaxFlag': '1',
            # 'ee': '2',
            # 'enPre': '1',
            # 'isFlushing': '2',
            # 'isUDPFlag': '1',
            # 'json': '1',
            # 'mType': 'full',
            # 'storeID': 'shoes',
            # 'triggerEvent': 'Twister',
            # 'twisterView': 'glance'
        }

        site = baseUrlHandle(url).getPlatformAndSite()['site'].lower()
        md5str = hashlib.md5(url.encode(encoding='UTF-8')).hexdigest()

        itemid_validity = ccAmazonCrawlService.commonRedisClass.zscoreValByKey('amazon_info_{}'.format(site),
                                                                               '{}'.format(md5str))
        now_time = time.time()
        # if itemid_validity != None:
        #     print('有缓存')
        #     shijiancha = int(now_time - itemid_validity)
        #     if shijiancha >= defaultApp.amazon_life_time['info']:
        #         print('已过期')
        #     else:
        #         print('没过期')
        #         print('http://47.107.142.65:9200/amazon_info/_doc/{itemid}'.format(itemid=md5str))
        #         data = self.commonElasticSearchClass.getSourceByIndexKey(index='amazon_info_{}'.format(site),
        #                                                                  doc_type="_doc",
        #                                                                  id=md5str)
        #         self.relayServiceClass.postProductCenterLinkJsonResult(data=data['product_data'])
        #         self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
        #
        #         variableList = data['product_data']['variableList']
        #         print('变体数:', len(variableList))
        #         companyCode = self.relayServiceClass.getProductCenterExtInfo()['companyCode']
        #         userId = self.relayServiceClass.getProductCenterExtInfo()['userId']
        #         # for v_data in variableList:
        #         #     executor.submit(self.post_small_data, self, v_data, companyCode, userId)
        #         tasklist = []
        #         for v_data in variableList:
        #             tasklist.append(gevent.spawn(self.post_small_data, site, v_data, companyCode, userId))
        #         gevent.joinall(tasklist)
        #         return
        # print('沒緩存')
        for useType in '01122':
            # print(useType)
            header['USETYPE'] = useType
            TARGETURL = url #+ '?language=en_US&th=1' if '?language=en_US&th=1' not in url else url
            header['TARGETURL'] = TARGETURL
            header['User-Agent'] = userAgent().getPc()

            try:
                result = WebRequest.easyGet(self=WebRequest, url=TARGETURL, header=header,
                                            timeout=5)
                html = result.text(self=WebRequest)

                print('html', len(html))
                data = self.setResult(site, html, url)  # 洗完的结构
                # print(666, json.dumps(data))

                if data:
                    self.relayServiceClass.postProductCenterLinkJsonResult(data=data['product_data'])
                    try:
                        self.commonElasticSearchClass.insertDataByIndexKey(index='amazon_info_{}'.format(site), id=md5str,
                                                                           data=data)

                        self.commonRedisClass.insertDataByIndexKey(redisKeyName='amazon_info_{}'.format(site), redisStr=md5str)
                    except Exception as e:
                        print(4444,e)
                    self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                    variableList = data['product_data']['variableList']
                    # print('variableList:', variableList)
                    if variableList == []:
                        return
                    else:
                        print('变体数:', len(variableList))
                        companyCode = self.relayServiceClass.getProductCenterExtInfo()['companyCode']
                        userId = self.relayServiceClass.getProductCenterExtInfo()['userId']
                        # for v_data in variableList:
                        #     executor.submit(self.post_small_data, self, v_data, companyCode, userId)

                        # all_task = []
                        # for future in as_completed(all_task):
                        #     data = future.result()
                        #     if data[0] == True:
                        #         pass
                        #     else:
                        #         executor.submit(self.post_small_data, data[1], data[2], data[3])  # 再發一次
                        tasklist = []
                        for v_data in variableList:
                            tasklist.append(gevent.spawn(self.post_small_data, site, v_data, companyCode, userId))
                        gevent.joinall(tasklist)

                        return
                else:
                    continue
            except Exception as e:
                print('error:', e)

    """
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """

    def setResult(self, site, sourceHtml, url):
        print(url)
        data = {
            'base': {
                "productId": "",
                "parent_identification": "",
                "variable_list": [],
                "title": "",
                "title_en": "",
                "brand": '',
                "sourceUrl": "",
                "site": "",
                "currency": "",
                "price": "",
                "priceRange": "",
                "siteLanguage": "zh",
                "business_years": "",  # 商家年限
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
                "comments_number": "",  # 评论数量
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

        html = etree.HTML(sourceHtml)

        var_obj_re = re.search("var obj = jQuery.parseJSON\('(.*?)'\);", sourceHtml)

        if var_obj_re == None:
            print('获取数据失败1')
            return
        json_data = var_obj_re.group(1)
        try:
            json_data_dict = json.loads(json_data)
        except:
            json_data_dict = json.loads(json_data.replace('\\', '\\\\'))

        parentAsin = json_data_dict['parentAsin']
        data['base']['parent_identification'] = parentAsin

        itemid = json_data_dict['mediaAsin']
        data['base']['productId'] = itemid

        print('itemid:', itemid)
        #################  新增   #######
        # 品牌，尺寸，重量，新增
        brand = ''
        weight = ''
        weight_unit = ''
        size = ''
        currency_mapping = {
            "": "",
            "￥": 'CNY',
            "CNY": "CNY",

            "$": "USD",
            "US$": "USD",
            "USD": "USD",

            "R$": "BRL",
            "BRL": "BRL",

            "THB": "THB",

            "£": 'GBP',
            "GBP": 'GBP',

            "€": 'EUR',
            "EUR": 'EUR',

            "₹": 'INR',
            "kr": 'SEK',

        }
        currency = ""
        brand_str = 'Brand,Brand Name;品牌;Marke;Marca;브랜드;العلامة التجارية;מותג'
        weight_str = 'Item Weight;Weight;商品重量;产品重量;Artikelgewicht;Peso do produto;Peso del producto;Artikelgewicht'
        site_str = 'Product Dimensions;Package Dimensions;Dimensiones del paquete;Dimensiones del producto;商品尺寸;Size;产品尺寸;包装尺寸;包裹尺寸;Dimensões do produto;Dimenses do produto;Dimensioni prodotto;Produktabmessungen;Verpackungsabmessungen;Item Dimensions LxWxH;Dimensões da embalagem;' \
                   '產品尺寸;패키지 크기;제품 치수;מידות המוצר;מידות חבילה;أبعاد الطرد;أبعاد الطرد;أبعاد المنتج'
        # 简短图文table
        detail_table = html.xpath(
            '//div[@class="a-row a-expander-container a-expander-inline-container"][2]//tr')
        if len(detail_table) < 1:
            detail_table = html.xpath(
                '//table[@class="a-normal a-spacing-micro"]/tr | //table[@id="product-specification-table"]/tr')

        for item in detail_table:
            th = item.xpath('.//th/text() | .//span[@class="a-size-base a-text-bold"]/text()')
            td = item.xpath('.//td/text() | .//span[@class="a-size-base"]/text()')
            if th and td:
                # print(th)
                # print(td)
                if str(th[0]) in brand_str:
                    brand = str(''.join(td)).strip()

                if str(th[0]) in weight_str:
                    weight = str(''.join(td)).strip()

                if str(th[0]) in site_str:
                    size = str(''.join(td)).strip()

        # 产品详情
        product_details = html.xpath(
            '//div[@id="detailBullets_feature_div"]/ul[@class="a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list"]/li')
        if len(product_details) < 1:
            product_details = html.xpath('//table[@id="productDetails_techSpec_section_1"]/tr | //table[@id="productDetails_detailBullets_sections1"]/tr')
        if len(product_details) < 1:
            product_details = html.xpath('//table[@id="productDetails_detailBullets_sections1"]/tr')
        for pd in product_details:
            pd_k = pd.xpath('./span[@class="a-list-item"]/span[@class="a-text-bold"]/text() | .//th/text()')
            pd_v = pd.xpath('./span[@class="a-list-item"]/span/text() | .//td/text()')

            if pd_k and pd_v:
                pd_k = str(pd_k[0]).replace('\u200f', '').replace('\u200e', '').replace(':', '').split('\n')
                pd_k = str(''.join(pd_k)).strip()
                pd_v = str(pd_v[-1]).replace('\u200f', '').replace('\u200e', '').split('\n')
                # print('pd_k:',pd_k)
                # print('pd_v:',pd_v)
                if len(brand) < 1 and pd_k in brand_str:
                    brand = str(''.join(pd_v)).strip()

                if len(size) < 1 and pd_k in site_str:
                    sizes = str(''.join(pd_v)).split(';')
                    size = sizes[0]
                    if len(sizes) >= 2:
                        weights = sizes[-1]
                        weight = str(weights).split(' ')[-2]
                        weight_unit = str(weights).split(' ')[-1]
                if len(weight) < 1 and pd_k in weight_str:
                    weights = str(''.join(pd_v)).split(' ')
                    weight = weights[0]
                    weight_unit = weights[-1]
        productDescription_xpath = html.xpath('//div[@id = "productDescription"]/p/text()')
        print(99999,productDescription_xpath)
        if productDescription_xpath:
            for item in productDescription_xpath:
                for ii in site_str.split(';'):
                    if ii in item:
                        size = str(item).split(':')[1]
                for ii in weight_str.split(';'):
                    if ii in item:
                        weight = str(item).split(':')[1]
                        weight_unit = str(item).split(' ')[-1]


        # 前台分类
        front_desk_types = html.xpath('//ul[@class="a-unordered-list a-horizontal a-size-small"]/li')
        front_desk_types_list = []
        for li in front_desk_types:
            front_desk_type_li = li.xpath('.//a/text()')
            if front_desk_type_li:
                front_desk_type_li = str(front_desk_type_li[0]).strip()
                front_desk_types_list.append(front_desk_type_li)
        data['base']['front_desk_type'] = '>'.join(front_desk_types_list)

        # 尺码表"size_table"
        size_tables = html.xpath('//a[@id="size-chart-url"]/@href')
        if size_tables:
            size_table = 'https://www.amazon.com/' + str(size_tables[0])
        else:
            size_table = ''
        data['base']['size_table'] = size_table

        # 价格区间
        priceRange_list = []
        priceRange_xp = html.xpath('//span[@id="priceblock_ourprice"]/text()')
        if priceRange_xp and '-' in priceRange_xp[0]:
            priceRange_xp = str(priceRange_xp).split('-')
            for i in priceRange_xp:
                v_price, currencys = self.split_price_currency(i,currency_mapping)
                if currencys and not currency:
                    currency = currencys
                priceRange_list.append(float(v_price))
        # 实际库存最大值
        stock_option = html.xpath('//select[@id="quantity"]//option')
        stock_option_lsit = []
        for option in stock_option:
            stock = option.xpath('./text()')
            stock = str(stock[0]).strip() if stock else ''
            stock_option_lsit.append(stock)
        # "product_rating": "",  # 商品评分
        product_rating = html.xpath('//span[@id="acrPopover"]/@title')
        if product_rating:
            product_rating = str(product_rating[0]).split(' ')[0] if product_rating else ''
            data['base']['product_rating'] = product_rating

        # "comments_number": 0,  # 评论数量
        comments_number = html.xpath('//span[@id="acrCustomerReviewText"]/text()')
        comments_number = str(comments_number[0]).split(' ')[0] if comments_number else ''

        data['base']['comments_number'] = comments_number

        stock = stock_option_lsit[-1] if stock_option_lsit else ''
        data['base']['stock'] = stock

        #################  新增   #######
        title = ""
        title_xpath = html.xpath('//*[@id="productTitle"]/text()')
        if title_xpath:
            title = title_xpath[0].replace('\n', '')
            data['base']['title_en'] = title


        price = ''

        pricetext_xpath = html.xpath(r'//span[re:match(@id, "priceblock_.*price")]/text()',
                                     namespaces={"re": "http://exslt.org/regular-expressions"})

        pricetext_xpath = pricetext_xpath if pricetext_xpath else html.xpath('//span[@id="price_inside_buybox"]/text()')
        if pricetext_xpath:
            pricetext = pricetext_xpath[0]
            pricetexts = pricetext.replace(' ', '').replace(',', '.').replace('\xa0', '').split('-')[0]

            # print('pricetexts:',pricetexts)
            price, currency = self.split_price_currency(pricetexts, currency_mapping)
            if price:
                data['base']['price'] = price
            if currency in currency_mapping:
                currency = currency_mapping[currency]
        if currency:
            data['base']['currency'] = currency

        data['base']['site'] = site
        siteLanguage_xpath = html.xpath('//input[@name ="askLanguage"]/@value')
        if siteLanguage_xpath:
            siteLanguage = siteLanguage_xpath[0]
            data['base']['siteLanguage'] = siteLanguage
        else:
            siteLanguage = re.findall('lang="(.*?)"', sourceHtml)
            if siteLanguage:
                data['base']['siteLanguage'] = siteLanguage[0]

        product_rating_xpath = html.xpath(
            '//div[@class="a-section a-spacing-none a-spacing-top-mini cr-widget-ACR"]/div[1]/div/div[2]/div/span/span/text()')
        if product_rating_xpath:
            product_rating_re = re.search('(\d+\.\d+)', product_rating_xpath[0])
            if product_rating_re:
                product_rating = product_rating_re.group(1)
                data['base']['product_rating'] = product_rating

        comments_number_xpath = html.xpath(
            '//div[@class="a-section a-spacing-none a-spacing-top-mini cr-widget-ACR"]/div[2]/span/text()')
        if comments_number_xpath:
            comments_number = comments_number_xpath[0].replace(' ', '').replace(',', '')
            comments_number_re = re.search('(\d+\.\d+|\d+).*?', comments_number)
            if comments_number_re:
                comments_number = comments_number_re.group(1)
                data['base']['comments_number'] = comments_number

        bulletPoint_xpath = html.xpath('//div[@id="featurebullets_feature_div"]//span[@class="a-list-item"]')
        bulletPoint_xpath_list = []
        for li_none in bulletPoint_xpath:
            li_none = li_none.xpath('./text()')
            if li_none:
                bulletPoint_xpath_list.append(str(li_none[0]).replace('\n', '').replace('\\n', '').strip())

        if bulletPoint_xpath_list:
            bulletPoint = '8-8=,=8-8'.join(bulletPoint_xpath_list)
            data['extension']['bulletPoint'] = bulletPoint

        imglist2 = []
        imglist_xpath = html.xpath('//div[@id="altImages"]/ul/li//span/img/@src')
        if len(imglist_xpath)<1:
            imglist_xpath = html.xpath('//div[@class="a-row a-spacing-mini a-spacing-top-micro"]//img/@src')
        img_jsons = re.search(re.compile("colorImages'?\"?: (.*?)colorToAsin", re.DOTALL), sourceHtml)


        try:
            all_img_re = re.search(re.compile("'colorImages': (.*?)colorToAsin", re.DOTALL), sourceHtml)
            all_data = all_img_re.group(1)

            img_json = json.loads(str(all_data).replace(' ', '').replace("'", '"')[:-3])
            for i,imgs in enumerate(img_json['initial']):
                image = imgs['hiRes'] if imgs.get('hiRes') else imgs.get('large')
                if i == 0:
                    img_i_data = {
                        "type": 0,
                        "imgUrl": image
                    }
                else:
                    img_i_data = {
                        "type": 2,
                        "imgUrl": image
                    }
                imglist2.append(img_i_data)
        except Exception as e:
            print("img:::",e)
        if imglist_xpath and len(imglist2)<1:
            for i, img_i in enumerate(imglist_xpath):
                if 'gif' in img_i or 'overlay' in img_i:
                    continue
                else:
                    if img_jsons:
                        try:
                            img_jsons = str(img_jsons.group()).split(' ', 3)[-1].split('\n')[0][:-2]
                        except:
                            img_jsons = ''
                        if img_jsons:
                            img_json = json.loads(img_jsons)
                            for i in img_json:
                                variant = i['thumb']
                                if img_i == variant:
                                    imgUrl = i['hiRes']
                                else:
                                    continue
                        else:
                            imgUrl = re.sub('._.*?_.*?_.jpg', '.800.jpg', img_i).replace('._SS40_', '')
                    else:
                        imgUrl = re.sub('._.*?_.*?_.jpg', '.800.jpg', img_i).replace('._SS40_', '')
                    if i == 0:
                        img_i_data = {
                            "type": 0,
                            "imgUrl": imgUrl
                        }
                    else:
                        img_i_data = {
                            "type": 2,
                            "imgUrl": imgUrl
                        }
                    imglist2.append(img_i_data)

        data['images'] = imglist2

        info2 = []
        info = html.xpath('//div[@class="a-column a-span6"]/div//div//tr')  # 一些列表属
        for attr_data in info:
            attr_data_i = filliter(attr_data.xpath('.//text()'))
            if attr_data_i:
                data_i = {
                    "productId": itemid,
                    "pkey": attr_data_i[0].replace('\n', ''),
                    "pval": attr_data_i[1],
                    "unit": ""
                }
                info2.append(data_i)
                if not weight and attr_data_i[0].replace('\n', '') in weight_str:
                    weights = attr_data_i[1].split(' ')
                    weight = weights[0]
                    weight_unit = weights[-1]

        data['attributes'] = info2
        data['base']['brand'] = brand
        data['base']['weight_value'] = str(weight).replace(weight_unit, '')
        data['base']['weight_unit'] = weight_unit
        data['base']['size'] = str(size).replace('x', '*')
        variableList2 = []
        # try:

        if 'dimensionValuesData' in sourceHtml or 'jQuery.parseJSON' in sourceHtml:
            style_name1, style_name2, style_name3, site_title_dict, name_id_dict, name_type_dict, title_img_dict = self.variable_html_re(
                sourceHtml)

            name_id_dict, id_price_dict, name_price_dict = self.variable_html_xpath(sourceHtml, name_id_dict)
            # print('style_name1:', style_name1)
            # print('style_name2:', style_name2)
            # print('style_name3:', style_name3)
            # print('name_id_dict:', name_id_dict)

            # print('name_type_dict:', name_type_dict)
            # print('title_img_dict:', title_img_dict)
            # print('\n')
            if style_name1 and style_name2 and style_name3:
                print('style_name333333333333333')
                for m, item1 in enumerate(style_name1):
                    for n, item2 in enumerate(style_name2):
                        for y, item3 in enumerate(style_name3):
                            attributes_i = []

                            productId, images_i = self.variable_id_img_from(item1, item2, item3, title_img_dict,
                                                                            name_id_dict, name_type_dict)

                            if item1 in name_id_dict:
                                productIds = name_id_dict[item1]
                                productId1 = productIds  + '1{}{}{}'.format(m, n, y)
                            else:
                                productId1 = str(itemid) + '1{}{}{}'.format(m, n, y)


                            if item2 in name_id_dict:
                                productIds = name_id_dict[item2]
                                productId2 = productIds + '2{}{}{}'.format(m, n, y)
                            else:
                                productId2 = str(itemid) + '2{}{}{}'.format(m, n, y)

                            if item3 in name_id_dict:
                                productIds = name_id_dict[item3]
                                productId3 = productIds + '3{}{}{}'.format(m, n, y)
                            else:
                                productId3 = str(itemid) + '3{}{}{}'.format(m, n, y)

                            if not productId:
                                productId = [productIds if productIds else str(itemid) + '{}{}{}'.format(m, n, y)][0]

                            if productId1 in id_price_dict:
                                v_price = id_price_dict[productId1]
                            elif productId2 in id_price_dict:
                                v_price = id_price_dict[productId2]
                            else:
                                v_price = price
                            if v_price:
                                priceRange_list.append(float(v_price))
                            base_i = {
                                "productId": productId + '{}{}{}'.format(n,m,y),
                                "parent_identification": str(parentAsin),
                                "title": str(title),
                                "currency": str(currency),
                                "price": v_price,
                                "stock": stock if itemid == productId else '',
                                "sales": ""
                            }
                            attri_i = {
                                "pkey": name_type_dict[item1],
                                "productId": productId1,
                                "pval": item1,
                                "unit": ""
                            }
                            attri_ii = {
                                "pkey": name_type_dict[item2],
                                "productId": productId2,
                                "pval": item2,
                                "unit": ""
                            }
                            attri_iii = {
                                "pkey": name_type_dict[item3],
                                "productId": productId3,
                                "pval": item3,
                                "unit": ""
                            }
                            attributes_i.append(attri_i)
                            attributes_i.append(attri_ii)
                            attributes_i.append(attri_iii)

                            varia_i = {
                                "base": base_i,
                                "attributes": attributes_i,
                                "images": images_i
                            }
                            variableList2.append(varia_i)

            elif style_name1 and style_name2:
                print('style_name2222222222222')
                for m, item1 in enumerate(style_name1):
                    for n, item2 in enumerate(style_name2):
                        attributes_i = []

                        productId, images_i = self.variable_id_img_from(item1, item2, '', title_img_dict, name_id_dict,
                                                                        name_type_dict)
                        if not productId:
                            print('not productId')
                            continue

                        productId1 = \
                        [name_id_dict[item1] if item1 in name_id_dict else str(itemid) + '1{}{}'.format(m, n)][0]
                        productId2 = \
                        [name_id_dict[item2] if item2 in name_id_dict else str(itemid) + '1{}{}'.format(m, n)][0]
                        if productId1 in id_price_dict:
                            v_price = id_price_dict[productId1]
                        elif productId2 in id_price_dict:
                            v_price = id_price_dict[productId2]
                        else:
                            v_price = price
                        if v_price:
                            v_price, currency = self.split_price_currency(v_price,currency_mapping)
                            priceRange_list.append(float(v_price))
                        base_i = {
                            "productId": productId + '{}{}'.format(n,m),
                            "parent_identification": str(parentAsin),
                            "title": str(title),
                            "currency": str(currency),
                            "price": v_price,
                            "stock": stock if itemid == productId else '',
                            "sales": ""
                        }
                        attri_i = {
                            "pkey": [name_type_dict[item1] if item1 in name_type_dict else ''][0],
                            "productId": productId1,
                            "pval": item1,
                            "unit": ""
                        }
                        attri_ii = {
                            "pkey": [name_type_dict[item2] if item2 in name_type_dict else ''][0],
                            "productId": productId2,
                            "pval": item2,
                            "unit": ""
                        }
                        attributes_i.append(attri_i)
                        attributes_i.append(attri_ii)

                        varia_i = {
                            "base": base_i,
                            "attributes": attributes_i,
                            "images": images_i
                        }
                        variableList2.append(varia_i)
            elif style_name1 or style_name2:
                print('style_name11111111')
                style_name3 = ''
                if style_name1:
                    style_name3 = style_name1
                if style_name2:
                    style_name3 = style_name2
                for i,item1 in enumerate(style_name3):
                    attributes_i = []
                    if item1 in name_id_dict:
                        productId1 = name_id_dict[item1]
                    else:
                        # print('productId1 not in name_id_dict')
                        continue
                    if productId1 in id_price_dict:
                        v_prices = id_price_dict[productId1]
                        v_price, currency = self.split_price_currency(v_prices, currency_mapping)

                    else:
                        v_price = price
                    if v_price:
                        priceRange_list.append(float(v_price))
                    base_i = {
                        "productId": str(item1) + '{}'.format(i),
                        "parent_identification": str(parentAsin),
                        "title": str(title),
                        "currency": str(currency),
                        "price": v_price,
                        "stock": stock if itemid == item1 else '',
                        "sales": ""
                    }
                    attri_i = {
                        "pkey": [name_type_dict[item1] if item1 in name_type_dict else ''][0],
                        "productId": productId1,
                        "pval": item1,
                        "unit": ""
                    }
                    attributes_i.append(attri_i)
                    if item1 in title_img_dict:
                        images_i = title_img_dict[item1]
                    else:
                        images_i = ''
                    varia_i = {
                        "base": base_i,
                        "attributes": attributes_i,
                        "images": images_i
                    }
                    variableList2.append(varia_i)

            elif not style_name1 and not style_name2 and name_price_dict:
                count = 0
                for k, v in name_price_dict.items():
                    attributes_i = []
                    productId = str(itemid) + '{}'.format(count)
                    count += 1
                    v_price, currency = self.split_price_currency(v, currency_mapping)

                    if v_price:
                        priceRange_list.append(float(v_price))
                    base_i = {
                        "productId": str(productId),
                        "parent_identification": str(parentAsin),
                        "title": str(title),
                        "currency": str(currency),
                        "price": v_price,
                        "stock": stock if itemid == productId else '',
                        "sales": ""
                    }
                    attri_i = {
                        "pkey": '',
                        "productId": productId,
                        "pval": k,
                        "unit": ""
                    }
                    attributes_i.append(attri_i)
                    images_i = ''
                    varia_i = {
                        "base": base_i,
                        "attributes": attributes_i,
                        "images": images_i
                    }
                    variableList2.append(varia_i)

            print('变体数：',len(variableList2))

        else:
            print('无变体数据')
        if price:
            priceRange_list.append(float(price))
        if priceRange_list and min(priceRange_list) != max(priceRange_list):
            priceRange = str(min(priceRange_list)) + '~' + str(max(priceRange_list))
        else:
            priceRange = price
        # except Exception as e:
        #     print('变体组装有问题：',e)

        data['base']['priceRange'] = priceRange
        if not data['base']['currency']:
            data['base']['currency'] = currency

        descriptionTextlist = []
        for attr_data in info:
            attr_data_i = filliter(attr_data.xpath('.//text()'))
            key = attr_data_i[0].replace('\n', '')
            value = attr_data_i[1]
            infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=key, value=value)
            descriptionTextlist.append(infostr)
        descriptionText = ''.join(descriptionTextlist)

        data['extension']['descriptionText'] = str(descriptionText).replace('<br>', '\n').replace('<br />', '\n')
        data['variableList'] = variableList2

        description, detail_html = get_description(html, site, itemid, parentAsin)
        # size, weight = self.parse_size_weight(detail_html, site_str, weight_str)

        # if not data['base']['size'] and size:
        #     data['base']['size'] = size[0]
        # if not data['base']['weight_value'] and weight:
        #     data['base']['weight_value'] = weight[0]

        data['extension']['description'] = descriptionText + description

        data2 = {
            "product_data": data,
            # "variableList": '',
        }

        return data2
        # desc_req = self.session.get(desc_url, headers=self.desc_headers, timeout=10)
        # result = self.parse_description(desc_req, product_data)
        # result_json = json.dumps(result)
        # sentinelServMaster.lpush(self.item_key, result_json)


    def split_price_currency(self, prices, currency_mapping):
        prices = str(prices).replace(',', '').replace(' ', '').replace('"', '').replace('\\xa0', '')
        v_price_i = re.findall('\d+.?\d+', prices)
        if v_price_i:
            v_price = v_price_i[0]
        else:
            v_price = ''
        if v_price:
            currency = ''.join(str(prices).split(v_price))
            currency = currency_mapping[currency] if currency in currency_mapping else currency
        else:
            currency = ''
        return v_price, currency

    def variable_id_img_from(self, item1, item2, item3, title_img_dict, name_id_dict, name_type_dict):
        if item1 and item2 and item3:
            if str(item1) + ' ' + str(item2) + ' ' + str(item3) in title_img_dict:
                key = str(item1) + ' ' + str(item2) + ' ' + str(item3)

            elif str(item1) + ' ' + str(item3) + ' ' + str(item2) in title_img_dict:
                key = str(item1) + ' ' + str(item3) + ' ' + str(item2)

            elif str(item2) + ' ' + str(item1) + ' ' + str(item3) in title_img_dict:
                key = str(item2) + ' ' + str(item1) + ' ' + str(item3)

            elif str(item2) + ' ' + str(item3) + ' ' + str(item1) in title_img_dict:
                key = str(item2) + ' ' + str(item3) + ' ' + str(item1)

            elif str(item3) + ' ' + str(item1) + ' ' + str(item2) in title_img_dict:
                key = str(item3) + ' ' + str(item1) + ' ' + str(item2)

            elif str(item3) + ' ' + str(item2) + ' ' + str(item1) in title_img_dict:
                key = str(item3) + ' ' + str(item2) + ' ' + str(item1)
                # print('item3 not in title_img_dict')
            elif str(item1) + ' ' + str(item2) in title_img_dict:
                key = str(item1) + ' ' + str(item2)
            elif str(item1) + ' ' + str(item3) in title_img_dict:
                key = str(item1) + ' ' + str(item3)
            elif str(item2) + ' ' + str(item3) in title_img_dict:
                key = str(item2) + ' ' + str(item3)

            else:
                key = ''
            images_i = ''
            if key and key in title_img_dict:
                images_i = title_img_dict[key]
            if not images_i and item1 in name_type_dict and item1 in name_type_dict:
                if name_type_dict[item1] == 'Color':
                    images_i = title_img_dict[item1]
            if not images_i and item2 in name_type_dict and item2 in title_img_dict:
                if name_type_dict[item2] == 'Color':
                    images_i = title_img_dict[item2]
            if not images_i and item3 in name_type_dict and item3 in title_img_dict:
                if name_type_dict[item3] == 'Color':
                    images_i = title_img_dict[item3]
            if not images_i:
                images_i = ''
            if key and key in name_id_dict:
                productId = name_id_dict[key]
            else:
                productId = ''

            return productId, images_i

        if item1 in name_id_dict:
            productId = name_id_dict[item1]
        elif item2 in name_id_dict:
            productId = name_id_dict[item2]
        else:
            productId = ''
        images_i = ''
        if item1 and item2 and not item3:

            for title_img_dict_key in title_img_dict:

                if item1 in title_img_dict:
                    images_i = title_img_dict[item1]
                    break
                elif item2 in title_img_dict:
                    images_i = title_img_dict[item2]
                    break
                if ';' in title_img_dict_key:
                    key = item1 + ';' + item2
                    if key not in title_img_dict:
                        key = item2 + ';' + item1

                    if key in title_img_dict:
                        images_i = title_img_dict[key]
                    else:
                        print('item2 not in title_img_dict')
                        images_i = ''
                    if key in name_id_dict:
                        productId = name_id_dict[key]

                elif ' ' in title_img_dict_key:

                    key = item1 + ' ' + item2
                    if key not in title_img_dict:
                        key = item2 + ' ' + item1

                    if key not in title_img_dict and '/' in item1 or '/' in item2:
                            key = item1 + ' ' + item2
                            key = str(key).replace('/', '\\/')
                            if key not in title_img_dict:
                                key = item2 + ' ' + item1
                            if key not in title_img_dict:
                                key = str(key).replace('/', '\\/')
                    if key and key in name_id_dict:
                        productId = name_id_dict[key]

                    if key in title_img_dict:
                        images_i = title_img_dict[key]
                    else:
                        images_i = ''
                        print('item1 not in title_img_dict:', key, ';', item1, ';', item2)
                else:
                    images_i = ''
                    print('title_img_dict组成有异样1', title_img_dict)

                break
        else:
            images_i = ''
            print('title_img_dict组成有异样', title_img_dict)

        return productId, images_i

    def variable_html_re(self, sourceHtml):
        var_obj_re = re.search("var obj = jQuery.parseJSON\('(.*?)'\);", sourceHtml)

        json_data = var_obj_re.group(1)
        try:
            json_data_dict = json.loads(json_data)
        except:
            json_data_dict = json.loads(json_data.replace('\\', '\\\\'))

        # 尺码与图片关系
        site_title_dict = {}
        dimensionValuesDisplayData = re.search(
            re.compile('dimensionValuesDisplayData.*?prioritizeReqPrefetch', re.DOTALL), sourceHtml)
        site_list = []  # 存在的尺码list
        name_id_dict = {}  # 字典：名称对应ID

        if dimensionValuesDisplayData:
            if '<div class' in dimensionValuesDisplayData.group(0):
                dimensionValuesDisplayData = re.search(
                    re.compile('dimensionValuesDisplayData" :.*?prioritizeReqPrefetch', re.DOTALL), sourceHtml)
            value_display = str(dimensionValuesDisplayData.group()).split(':', 1)[-1].split('\n')[0][:-1]

            # print('尺码,标题,ID关系', value_display)
            value_display_json = json.loads(value_display)

            # 提取库存关系
            for k, v in value_display_json.items():
                name_id_dict[v[0]] = k
                name_id_dict[v[-1]] = k
                site_list.append((v[0], v[-1]))

            # 库存量构造字典
            for i in site_list:
                key = i[0]
                if key in site_title_dict:
                    site_title_dict[key].append(i[1])  # 向对应值的列表中添加新元素
                else:
                    site_title_dict[key] = [i[1]]  # 第一次出现的值构造为列表，方便下次放元素

        print('对应的库存site_title_dict', site_title_dict)

        title_img_dict = {}  #
        dimensionValuesData = re.search(re.compile('dimensionValuesData.*?asinToDimensionIndexMap', re.DOTALL),
                                        sourceHtml)
        # 提取图片的key和value
        if dimensionValuesData:
            # asinToDimensionIndexMap = str(dimensionValuesData.group()).split(':', 1)[-1].split('\n')[0][:-1]
            # asinToDimensionIndexMap = eval(asinToDimensionIndexMap)

            if 'colorImages' in json_data_dict:
                for index in json_data_dict['colorImages']:
                    img_urls = json_data_dict['colorImages'][index]
                    img_lsit = []
                    for img_url in img_urls:
                        if img_url.get('hiRes'):
                            imgUrl = img_url.get('hiRes')
                        else:
                            imgUrl = img_url.get('large')
                        img_i = {
                            "type": "3",
                            "imgUrl": imgUrl
                        }
                        img_lsit.append(img_i)
                    title_img_dict[index] = img_lsit

            else:
                print('没有colorImages')
        else:
            print('没有dimensionValuesData')
        # print('标题与橱窗图关系title_img_dict', json.dumps(title_img_dict))
        # print('', len(title_img_dict))
        # print('name_id_dict:', json.dumps(name_id_dict))
        # print('\n')

        # 名称,ID
        dimensionValuesDisplayData_re = re.search(
            re.compile('dimensionValuesDisplayData"\'? : (.*?)"\'?pwASINs', re.DOTALL), sourceHtml)
        if dimensionValuesDisplayData_re:

            dimensionValuesDisplayData = str(dimensionValuesDisplayData_re.group(1)).strip()
            dimensionValuesDisplayData = eval(dimensionValuesDisplayData[:-1] if dimensionValuesDisplayData[-1] == "," else dimensionValuesDisplayData[:-2])
            for k, v in dimensionValuesDisplayData.items():
                if isinstance(v, list):
                    value = ' '.join(v)
                    name_id_dict[value] = k
                    for i in v:
                        name_id_dict[i] = k

        # 名称，类型，id
        variationDisplayLabels = re.search(
            re.compile('variationDisplayLabels"\'? : (.*?)"\'?dimensionHierarchyData', re.DOTALL), sourceHtml)
        if variationDisplayLabels:
            variationValue_type_dict = str(variationDisplayLabels.group(1)).strip()
            variationValue_type_dict = eval(variationValue_type_dict[:-1] if variationValue_type_dict[-1] == "," else variationValue_type_dict[:-2])
        else:
            variationValue_type_dict = ''

        name_type_dict = {}
        style_name1 = []
        style_name2 = []
        style_name3 = []
        # 库存
        style_name_list = []
        variationValues = re.search(re.compile('variationValues"\'? : (.*?)\'?"asinVariationValues', re.DOTALL),
                                    sourceHtml)
        if variationValues:
            variationValue_str = str(variationValues.group(1)).strip()
            variationValue_dict = eval(str(variationValue_str)[:-1] if variationValue_str[-1] == ',' else variationValue_str[:-2])
            count = 0
            for k, v in variationValue_dict.items():

                if k in variationValue_type_dict:
                    name = variationValue_type_dict[k]
                    for vv in v:
                        name_type_dict[vv] = name
                else:
                    print('名称类型不在variationValue_type_dict里')

                # 获取样式列表
                if len(variationValue_dict) == 1:
                    style_name1 = v
                elif len(variationValue_dict) == 2:
                    if count == 0:
                        style_name1 = v
                        count += 1
                    elif count == 1:
                        style_name2 = v
                elif len(variationValue_dict) == 3:
                    if count == 0:
                        style_name1 = v
                        count += 1
                    elif count == 1:
                        style_name2 = v
                        count += 1
                    elif count == 2:
                        style_name3 = v
                style_name_list.append(v)
        else:
            print('not variationValues')

        return style_name1, style_name2, style_name3, site_title_dict, name_id_dict, name_type_dict, title_img_dict

    def variable_html_xpath(self, sourceHtml, name_id_dict):
        html = etree.HTML(sourceHtml)

        variation_color_name = html.xpath(
            '//ul[@class="a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare imageSwatches"]/li')
        for li_xp in variation_color_name:
            variation_id = li_xp.xpath('./@data-defaultasin')
            variation_title = li_xp.xpath('.//img/@alt')
            if variation_id and variation_title:
                if variation_id[0] not in name_id_dict:
                    name_id_dict.update({variation_id[0]: variation_title[0]})
                else:
                    pass
                    # print('variation_id[0] in name_id_dict')
        # name,id
        variation_size_name = html.xpath(
            '//ul[@class="a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare"]/li')
        for li_xp in variation_size_name:
            variation_id = li_xp.xpath('./@data-defaultasin')[0]

            if not variation_id:
                variation_id = li_xp.xpath('./@data-dp-url')
                if variation_id:
                    variation_re = str(variation_id).split('/')
                    variation_id = variation_re[2]
                    # print('variation_re:::::::::',variation_re[1])
            variation_title = li_xp.xpath('.//p[@class="a-text-left a-size-base"]/text()')
            # print('variation_id:', variation_id)
            # print('variation_title:', variation_title)
            if variation_id and variation_title:
                if variation_id not in name_id_dict:
                    name_id_dict.update({variation_id: variation_title[0]})

        id_price_dict = {}
        name_price_dict = {}
        # 获取每个变体名上的价格
        variable_html = html.xpath(
            '//ul[@class="a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare"]/li | //ul[@class="a-unordered-list a-nostyle a-button-list a-declarative a-button-toggle-group a-horizontal a-spacing-top-micro swatches swatchesSquare imageSwatches"]/li | //ul[@class="a-unordered-list a-nostyle a-button-list a-horizontal"]/li')

        for variable_xp in variable_html:
            price_re = ''
            price_xp = variable_xp.xpath(
                './/p[@class="a-spacing-none a-text-left a-size-mini twisterSwatchPrice"]/text()')

            options_id = variable_xp.xpath('./@data-defaultasin')
            # print('options_id:', options_id)
            if price_xp:
                id_price_dict[options_id[0]] = price_xp[0]

            if not price_xp:
                price_xp = variable_xp.xpath(
                    './/span[@class="a-size-base a-color-secondary"]/text() |.//span[@class="a-size-base a-color-price a-color-price"]/text()')
            if not price_xp:
                price_xp = variable_xp.xpath(
                    './/span[@class="a-color-base"]/text() |.//span[@class="a-color-secondary"]/text()')
                if price_xp:
                    price_xp = list(''.join(price_xp).replace('\n', '').replace('\\n', ''))

            if not price_xp:
                price_xp = variable_xp.xpath('.//span[@class="a-color-price"]/text()')

            if not price_xp:
                price_xp = variable_xp.xpath('.//span[@class="a-size-mini olpWrapper"]/text()')
            if not price_xp:
                price_xp = variable_xp.xpath('.//div[@class="twisterSlotDiv addTwisterPadding"]//span/text()')

            if price_xp:
                price_re = re.findall('\$?\d+.?,?\d+\$?', ','.join(price_xp))
                # print('variable_pr:', price_re)
                if price_re and options_id:
                    id_price_dict[options_id[0]] = price_re[0]
                # else:

            variable_titles = variable_xp.xpath('.//span[@class="a-button-inner"]/a/span[1]/text()')
            if variable_titles:
                variable_titles = ''.join(variable_titles).replace('\n', '').replace('\\n', '')

            if not variable_titles:
                variable_titles = variable_xp.xpath('.//span[@class=""]/text()')

            if variable_titles:
                print('variable_titles:', variable_titles)
                variable_title = str(''.join(variable_titles)).replace('\n', '').replace('\\n', '')
                if options_id and variable_title and options_id not in name_id_dict:
                    name_id_dict.update({options_id[0]: variable_title})
            else:
                variable_title = ''

            if price_re and variable_title and not name_id_dict:
                name_price_dict[variable_title] = price_re[0]
        # print('img_order_list:', img_order_list)

        # print('id_price_dict:', id_price_dict)
        # print('name_price_dict:', name_price_dict)

        return name_id_dict, id_price_dict, name_price_dict


    def judgeCommodityTrend(goodsDescript):
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