# coding: utf-8
import itertools
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

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


def get_sku_mapping(HTML):
    prop_xpath_a_k = HTML.xpath(
        "//div[@class='detailed_info']/div[@class='default-size size_box']/div[1]/span[1]/text()")  # 尺码
    prop_xpath_a_v = HTML.xpath(
        "//div[@class='detailed_info']/div[@class='default-size size_box']/div[1]/span[2]/a/text()")  # 尺码
    prop_xpath_a = list(itertools.product(prop_xpath_a_k, prop_xpath_a_v))
    prop_xpath_b_k = HTML.xpath("//div[@class='detailed_info']/div[@class='color_box']/div[1]/text()")  # 颜色
    prop_xpath_b_v = HTML.xpath(
        "//div[@class='detailed_info']/div[@class='color_box']/div[@class='color_item sku-color']/p/text()")  # 颜色
    prop_xpath_b = list(itertools.product(prop_xpath_b_k, prop_xpath_b_v))
    sku_mapping = list(itertools.product(prop_xpath_a, prop_xpath_b))

    return sku_mapping


def get_location(HTML):
    location = ''
    main = HTML.xpath('//div[@class="site_right"]//div')
    for i in main:
        name = i.xpath('./b/text()')[0]
        name_value = i.xpath('./text()')[0]
        if name == '地址':
            location = name_value
    return location


class ccBao66CrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Bao66'

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

        md5str = hashlib.md5(url.encode(encoding='UTF-8')).hexdigest()
        itemid_validity = commonRedisClass.zscoreValByKey('bao66_info', '{}'.format(md5str))
        now_time = time.time()
        if itemid_validity != None:
            print('有缓存')
            shijiancha = int(now_time - itemid_validity)
            if shijiancha >= defaultApp.bao66_life_time['info']:
                print('已过期')
            else:
                print('没过期')
                print('http://47.107.142.65:9200/bao66_info/_doc/{itemid}'.format(itemid=md5str))
                data = commonElasticSearchClass.getSourceByIndexKey(index='bao66_info', doc_type="_doc", id=md5str)
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)

                return

        header = {}
        for useType in '0111222':
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            header['User-Agent'] = userAgent().getPc()
            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,timeout=5)
                result_data = result.text(self=WebRequest)
                data = self.setResult(result_data, url)  # 洗完的结构
                print(666, data)
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                commonElasticSearchClass.insertDataByIndexKey(index='bao66_info', id=md5str, data=data)
                commonRedisClass.insertDataByIndexKey(redisKeyName='bao66_info', redisStr=md5str)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                return
            except Exception as e:
                print(e)

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
        data = {
            'base': {
                "productId": "",
                "title": "",
                "brand": '',
                "sourceUrl": "",
                "site": "",
                "currency": "CNY",
                "price": "",
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
                "sales": "",  # 销量
                "collection_volume": "",  # 收藏量
                "praise_rate": "",  # 好评率
                "product_rating": "",  # 商品评分
                "comments_number": 0,  # 评论数量
                "quantity": 0,
                "mall_id": "",
                "mall_link": "",
                "mall_name": ""
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

        HTML = etree.HTML(sourceHtml)

        itemid = ""
        itemid_xpath = HTML.xpath('//input/@data-product_id')
        if itemid_xpath:
            itemid = itemid_xpath[0]
            data['base']['itemid'] = itemid

        title = ""
        title_xpath = HTML.xpath('//div[@class="title"]/div/text()')
        if title_xpath:
            title = title_xpath[0]
            data['base']['title'] = title

        location = get_location(HTML)
        data['base']['location'] = location
        # sellerid = str(all_data_dict['rateConfig']['sellerId'])
        # # sellerNick = all_data_dict['itemDO']['sellerNickName']

        # mall_id = str(all_data_dict['rstShopId'])
        yuanjia = ""
        yuanjia_xpath = HTML.xpath("//div[@class='massage']/span[2]/span[2]/text()")
        if yuanjia_xpath:
            yuanjia = yuanjia_xpath[0]
            data['base']['price'] = yuanjia

        mall_link_xpath = HTML.xpath('//div[@class="business"]/div[@class="name_left"]//a/@href')
        if mall_link_xpath:
            mall_link = mall_link_xpath[0]
            data['base']['mall_link'] = mall_link

        mall_name_xpath = HTML.xpath('//div[@class="business"]/div[@class="name_left"]//a/@title')
        if mall_name_xpath:
            mall_name = mall_name_xpath[0]
            data['base']['mall_name'] = mall_name

        collection_volume_xpath = HTML.xpath("//div[@class='renqi_box']/span[1]/span/text()")
        if collection_volume_xpath:
            try:
                collection_volume = int(collection_volume_xpath[0])
            except:
                collection_volume =""
            data['base']['collection_volume'] = collection_volume

        imglist2 = []
        images_xpath = HTML.xpath('//ul[@class="tb-thumb"]/li/div/a/img/@src')
        print('images_xpath',images_xpath)
        if images_xpath:
            for i in images_xpath:
                img_i = {
                    "type": "0",
                    "imgUrl": i,
                }
                imglist2.append(img_i)

            detillimg = HTML.xpath(
                '///div[@class="product_details"]/div[@style="text-align:center;margin-top:15px"]/img/@data-url')
            for i in detillimg:
                img_i = {
                    "type": "1",
                    "imgUrl": i,
                }
                imglist2.append(img_i)
        data['images'] = imglist2
        info2 = []
        propsCut_data_name_k = HTML.xpath('//div[@class="shoes_info"]/span/text()')
        propsCut_data_name_v = HTML.xpath('//div[@class="shoes_info"]/span/a/text()')
        propsCut_data_name = tuple(zip(propsCut_data_name_k, propsCut_data_name_v))
        for attr_data in propsCut_data_name:
            data_i = {
                "productId": str(itemid),
                "pkey": attr_data[0],
                "pval": attr_data[1],
                "unit": ""
            }
            info2.append(data_i)
        data['attributes'] = info2

        variableList2 = []
        sku_mapping = get_sku_mapping(HTML)
        for prop_i in sku_mapping:
            base_i = {
                "productId": str(itemid),
                "title": title,
                "currency": "CNY",
                "price": float(yuanjia),
                "priceRange": '',
                "stock": '',
                "sales": ''
            }
            attributes_i = []
            for j in prop_i:
                attr_i = {
                    "pkey": j[0],
                    "productId": str(itemid),
                    "pval": j[1],
                    "unit": ""
                }
                attributes_i.append(attr_i)
            pdata = {
                "base": base_i,
                "attributes": attributes_i,
                "images": []
            }
            variableList2.append(pdata)

        descriptionText =""
        descriptionText_xpath = HTML.xpath("//div[@class='info_list']")
        if descriptionText_xpath:
            descriptionText = etree.tostring(descriptionText_xpath[0]).decode()
            data['extension']['descriptionText'] = descriptionText

        description_xpath = HTML.xpath("//div[@class='product_details']")
        if description_xpath:
            description = etree.tostring(description_xpath[0]).decode().replace(
                '"/public/pages/img/loading/scrollLoading_750.gif" data-url=', '')
            data['extension']['description'] =descriptionText+ description

        # print(json.dumps(product_data))
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
