# -*- coding: utf-8 -*-
# from gevent import monkey

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
    print('pricetext:', pricetext)
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
    for i in data:
        if '"FeatureName" : "productDescription_feature_div' in i:
            info2_html = '<h2>' + json.loads(i.replace('  ', ''))['Value']['content'][
                'productDescription_feature_div'].replace('\n', '').replace('\r', '')
            break
    return info2_html


def get_info2_html(data):
    info_html = ""
    for i in data:
        if '"FeatureName" : "productDetails_feature_div' in i:
            info_html = json.loads(i.replace('  ', ''))['Value']['content'][
                'productDetails_feature_div'].replace('\n', '').replace('\r', '')
            break
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
    descriptionDiv1Ids = [
        'aplus3p_feature_div',
        'btf-content-1_feature_div',
        'dp_productDescription_container_div',
        'aplus3p_feature_div',
        'dpx-aplus-product-description_feature_div',
        'dpx-aplus-3p-product-description_feature_div',
        'dp-container',
        'dpx-aplus-brand-story_feature_div',
    ]
    for id in descriptionDiv1Ids:
        desc1_xpath = html.xpath('//div[@id="'+id+'"]')
        if desc1_xpath:
            desc1 = etree.tostring(desc1_xpath[0]).decode()
            desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
            desc1 = desc1.replace('\n', '').replace('\r', '')
            print(desc1)
            if len(desc1) > 500:
                break

    if desc1 == "":
        desc = get_desc(site, itemid, parentAsin)
        desc1 = get_info_html(desc)
        print(777)


    descriptionDiv2Ids = [
        'detailBullets',
        'product-details-grid_feature_div',
        'detailBullets_feature_div',
    ]

    for id2 in descriptionDiv2Ids:
        desc2_xpath = html.xpath('//div[@id="'+id2+'"]')
        if desc2_xpath:
            desc2 = etree.tostring(desc2_xpath[0]).decode()
            desc2 = desc2.replace('\n', '').replace('\r', '')

    # if desc2 == "":
    #     desc = get_desc(site, itemid, parentAsin)
    #     desc2 = get_info2_html(desc)

    description = desc1 + desc2
    print(22222, description)
    return description


def get_desc(site, sku, psku):
    domain = defaultApp.amz_domain_mapping[site.lower()]

    now_skuid = sku
    parentAsin = psku
    url = "{domain}/gp/page/refresh?acAsin={now_skuid}&asinList={now_skuid}&auiAjax=1&dcm=1&dpEnvironment=hardlines&dpxAjaxFlag=1&ee=2&enPre=1&id={now_skuid}&isFlushing=2&isUDPFlag=1&json=1&parentAsin={parentAsin}&pgid=pc_display_on_website&ptd=COMPUTER_DRIVE_OR_STORAGE&triggerEvent=Twister".format(
        domain=domain, now_skuid=now_skuid, parentAsin=parentAsin)
    header = {
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    for useType in '01111112':
        print(useType)
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
            print(e)


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
            if itemid_validity != None:
                print('有缓存_v')
                shijiancha = int(now_time - itemid_validity)
                if shijiancha >= defaultApp.amazon_life_time['info']:
                    print('已过期_v')
                else:
                    print('没过期_v')
                    print('http://47.107.142.65:9200/amazon_info_v/_doc/{itemid}'.format(itemid=md5str))
                    result = self.commonElasticSearchClass.getSourceByIndexKey(index='amazon_info_v_{}'.format(site),
                                                                               doc_type="_doc",
                                                                               id=md5str)
                    result = json.loads(result['datajson'])
                    result['companyCode'] = ccode
                    result['userId'] = uuid
                    requests.post(defaultApp.productCenterUrl + 'api/product/crawler/large/variation',
                                  data=json.dumps(result), timeout=2)
                    flag = [True]
                    return flag
            print('没缓存_v')
            desc_data = get_desc(site, now_skuid, parentAsin)
            pricetext = get_pricetext(desc_data)
            print(666)
            # print('post_small_data',pricetext)
            if pricetext:
                pricetext = pricetext.replace(' ', '').replace(',', '.').replace('\xa0', '').split('-')[0]
                price = re.search('.*?(\d+\.\d+).*?', pricetext).group(1)
            else:
                price = ''
            stock = get_stock(desc_data)
            data['base']["price"] = str(price)
            data['base']["stock"] = str(stock)
            data = {"data": {"list": [{'variableList': [data]}]}}
            es_data = {
                'id': md5str,
                'datajson': json.dumps(data),
                'type': 'amazon_info_v_{}'.format(site),
                'updated_time': str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
            }
            self.commonElasticSearchClass.insertDataByIndexKey(index='amazon_info_v_{}'.format(site), id=md5str,
                                                               data=es_data)
            self.commonRedisClass.insertDataByIndexKey(redisKeyName='amazon_info_v_{}'.format(site), redisStr=md5str)

            data['companyCode'] = ccode
            data['userId'] = uuid
            requests.post(defaultApp.productCenterUrl + 'api/product/crawler/large/variation', data=json.dumps(data),
                          timeout=2)

            flag = [True]
            print('v+1:', '666')
        except Exception as e:
            flag = [False, data, ccode, uuid]
            print('v-1:', e)
        return flag

    def saveHtmlResult(self, data):
        site = data['site']

        domain = defaultApp.amz_domain_mapping[site.lower()]

        what_asin = data['asin_list'][0]

        url =  '{}/dp/{}'.format(domain,what_asin)

        header = {
            'accept': 'text/html,*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'cookie': 'session-id=144-4054991-2800846; session-id-time=2082787201l; i18n-prefs=USD; lc-main=zh_CN; sp-cdn="L5Z9:CN"; ubid-main=134-6787062-1625066; session-token=3LM6xDx/5dnXDmH2OrPC/uzjhB6rWfdS1/GEKG5OH+z27WYX6Eq7KhW/MrYPKRq/kSDY0WuPKogk0KLMmh+X6sNecf627GUlgAQ9BketgogadRlEICMRoxx9Q0IQhoTpxdxqPtXY/Af/nMxcPGH5Dw5Jt2Jm7HIFO8jhMy+Qf+xTXK/mCCjqH886mjuDCiGs; csm-hit=tb:468826Z7M1PVP9Y5R5GT+s-TM8S0ZDG15SV0MZ6K818|1619078290003&t:1619078290003&adb:adblk_no; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:CN"; ubid-main=132-5043066-6035737; session-id=140-0976175-1923942; lc-main=zh_CN; session-token=gY5hmFq+U6it0pYJDfJqCquoi233F0h2bpOaRWxwlidPPqXwYvOTgPAEPXrh3RDefvjeEJCPTL0plYg8TkX/GgI8NfqPQj2iXLoHwChHZTeqZq38TrI6BTXhsu/PsJ3oPP5v7f/BiTXIWsyo9IMCdUE9TR6GUXZhkZoKl1fvy2xE7YrnGa4TdKOsyzfeopPO',
            'cache-control': 'max-age=0',
            'downlink': '10',
            'ect': '4g',
            'referer': 'https://www.amazon.com/-/szh/dp/B07KFZ77QD/ref=twister_B084YYBL7G?th=1',
            'rtt': '200',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
            'auiAjax': '1',
            'dpEnvironment': 'softlines',
            'dpxAjaxFlag': '1',
            'ee': '2',
            'enPre': '1',
            'isFlushing': '2',
            'isUDPFlag': '1',
            'json': '1',
            'mType': 'full',
            'storeID': 'shoes',
            'triggerEvent': 'Twister',
            'twisterView': 'glance'
        }

        for useType in '01310310333':
            try:
                header['USETYPE'] = useType
                TARGETURL = url + '?language=en_US&th=1' if '?language=en_US&th=1' not in url else url
                header['TARGETURL'] = TARGETURL
                header['User-Agent'] = userAgent().getPc()

                result = WebRequest.easyGet(self=WebRequest, url=TARGETURL, header=header,
                                            timeout=3)

                html = result.text(self=WebRequest)
                if len(html) < 10000:
                    continue
                elif html == None:
                    continue
                return  html

            except Exception as e:
                print(e)
                continue
        return None

    """
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """


    def setResult(self, site,sourceHtml):
        data = {
            "marketplace_url": '',
            "site": '',
            "asin": '',
            "image": '',
            "images": [],
            "product_attr": {},
            "title": '',
            "infos": '',
            "review_star": '',
            "review_num": '',
            "bullet_point": '',
            "vasin": [],
            "descriptionText": '',
            "description": ''
        }

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

        data['site'] = site

        domain = defaultApp.amz_domain_mapping[site.lower()]
        data['marketplace_url'] = domain

        parentAsin = json_data_dict['parentAsin']

        itemid = json_data_dict['mediaAsin']
        data['asin'] = itemid

        title = ""
        title_xpath = html.xpath('//*[@id="productTitle"]/text()')
        if title_xpath:
            title = title_xpath[0].replace('\n', '')
        data['title'] = title

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
        data['infos'] = info2

        product_rating_xpath = html.xpath(
            '//div[@class="a-section a-spacing-none a-spacing-top-mini cr-widget-ACR"]/div[1]/div/div[2]/div/span/span/text()')
        if product_rating_xpath:
            product_rating_re = re.search('(\d+\.\d+)', product_rating_xpath[0])
            if product_rating_re:
                product_rating = product_rating_re.group(1)
                data['review_star'] = product_rating

        comments_number_xpath = html.xpath(
            '//div[@class="a-section a-spacing-none a-spacing-top-mini cr-widget-ACR"]/div[2]/span/text()')
        if comments_number_xpath:
            comments_number = comments_number_xpath[0].replace(' ', '').replace(',', '')
            comments_number_re = re.search('(\d+\.\d+|\d+).*?', comments_number)
            if comments_number_re:
                comments_number = comments_number_re.group(1)
                data['review_num'] = comments_number

        bulletPoint_xpath = html.xpath('//div[@id="featurebullets_feature_div"]/div/ul/li/span/text()')
        if bulletPoint_xpath:
            bulletPoint_list = filliter(bulletPoint_xpath)
            bulletPoint = '8-8=,=8-8'.join(bulletPoint_list)
            data['bullet_point'] = bulletPoint

        imglist2 = []
        imglist_xpath = html.xpath('//div[@id="altImages"]/ul/li//span/img/@src')
        if imglist_xpath:
            for img_i in imglist_xpath:
                if 'gif' in img_i:
                    continue
                else:
                    imgUrl = re.sub('._.*?_.*?_.jpg', '.800.jpg', img_i).replace('._SS40_', '')
                    imglist2.append(imgUrl)
            if imglist2:
                data['images'] = imglist2
                data['image'] = imglist2[0]

        variableList2 = []

        dimensionValuesDisplayData = re.search('"dimensionValuesDisplayData".*({.*?}),', sourceHtml)
        if dimensionValuesDisplayData != None:

            dimensionsDisplay = re.search('"dimensionsDisplay".*(\[.*?\]),', sourceHtml).group(1)

            # print(dimensionValuesDisplayData)
            # print(dimensionsDisplay)

            colorImages_new = {}
            colorImages = json_data_dict['colorImages']
            for k, v in colorImages.items():
                colorImages_new.update({k.replace('\\', ''): v})

            dimensionValuesDisplayData_dict = json.loads(dimensionValuesDisplayData.group(1))

            for k, v in dimensionValuesDisplayData_dict.items():
                base_i = {
                    "vasin": str(k),
                    "vtitle": str(title),
                    "vimage": '',
                    "vimages": [],
                    "vproduct_attr": ''
                }
                vv = tuple(zip(dimensionsDisplay.split(','), v))
                # print(vv)
                vproduct_attr = {}
                for j in vv:
                    attr_k = j[0].replace('"', '').replace('[', '').replace(']', '').replace("\\r", '').replace("\\n",
                                                                                                                '').replace(
                        '\\', '')
                    attr_v = j[1]
                    vproduct_attr.update({attr_k: attr_v})
                    try:
                        cctimgmapping = colorImages_new[attr_v]
                        base_i['vimage'] = colorImages_new[attr_v][0]['large']
                        base_i['vimages'] = [i['large'] for i in cctimgmapping]
                    except KeyError:
                        continue

                base_i["vproduct_attr"] = vproduct_attr
                variableList2.append(base_i)


        data['vasin'] = variableList2

        descriptionTextlist = []
        for attr_data in info:
            attr_data_i = filliter(attr_data.xpath('.//text()'))
            key = attr_data_i[0].replace('\n', '')
            value = attr_data_i[1]
            infostr = '<li title="{value}">{key}:&nbsp;{value}</li>'.format(key=key, value=value)
            descriptionTextlist.append(infostr)

        descriptionText = '<ul>' + ''.join(descriptionTextlist) + '</ul>'
        data['descriptionText'] = descriptionText

        description = get_description(html, site, itemid, parentAsin)
        data['description'] = descriptionText + description

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
