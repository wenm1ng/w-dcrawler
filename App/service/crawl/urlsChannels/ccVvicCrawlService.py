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


class ccVvicCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Vvic'

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
        itemid_validity = commonRedisClass.zscoreValByKey('vvic_info', '{}'.format(md5str))
        now_time = time.time()
        if itemid_validity != None:
            print('有缓存')
            shijiancha = int(now_time - itemid_validity)
            if shijiancha >= defaultApp.soukuan_life_time['info']:
                print('已过期')
            else:
                print('没过期')
                print('http://47.107.142.65:9200/vvic_info/_doc/{itemid}'.format(itemid=md5str))
                data = commonElasticSearchClass.getSourceByIndexKey(index='vvic_info', doc_type="_doc", id=md5str)
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)

                return

        header = {}
        for useType in '0111222':
            header['USETYPE'] = useType
            header['referer'] = url
            header['user-agent'] = userAgent().getPc(),
            header['TARGETURL'] = url.replace('/recommend', '')  # 去除活动标签
            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                            timeout=2)
                data = self.setResult(result.text(self=WebRequest), url)  # 洗完的结构
                print(666, data)
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                commonElasticSearchClass.insertDataByIndexKey(index='vvic_info', id=md5str, data=data)
                commonRedisClass.insertDataByIndexKey(redisKeyName='vvic_info', redisStr=md5str)
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

        html = etree.HTML(sourceHtml)

        title = ''
        title_xpath = html.xpath("//h1[@class='detail-title']/text()")
        if title_xpath:
            title = title_xpath[0].replace('\n', '').replace('\r', '').replace(' ', '')
            data['base']['title'] = title

        script_info = re.findall(r'<script>(.*?)</script>', sourceHtml, re.S | re.M)  # 正则拿出所有<script>
        shop_script_info = script_info[-2]
        mallId_re = re.search("_SHOPID = '(\d+)';", shop_script_info)
        if mallId_re:
            mall_id = mallId_re.group(1)
            data['base']['mall_id'] = mall_id
            data['base']['mall_link'] = 'https://www.vvic.com/shop/{}'.format(mall_id)

        item_script_info = script_info[3]

        itemid = ""
        itemid_re = re.search("_ITEMID = '(\d+)';", item_script_info)
        if itemid_re:
            itemid = itemid_re.group(1)
            data['base']['productId'] = itemid

        price = ''
        price_re = re.search("_DISCOUNTPRICE = '(.*?)';", item_script_info)
        if price_re:
            price = price_re.group(1)
            data['base']['price'] = price

        variableList2 = []
        skuinfo_re = re.search("_SKUMAP = '(.*?)';", item_script_info)
        if skuinfo_re:
            skuinfo = skuinfo_re.group(1)
            print(6666666, skuinfo)
            for variable_data in json.loads(skuinfo):
                base_i = {
                    "productId": variable_data['id'],
                    "title": str(title),
                    "currency": "CNY",
                    "price": variable_data['discount_price'],
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

                sku_imglist = []
                img_data = {
                    "type": "3",
                    "imgUrl": variable_data['color_pic']
                }
                sku_imglist.append(img_data)

                varia_i = {
                    "base": base_i,
                    "attributes": attributes_i,
                    "images": sku_imglist
                }
                variableList2.append(varia_i)
        data['variableList'] = variableList2

        sales_xpath = html.xpath("//ul[@class='detail-amount']/li[1]/text()")
        if sales_xpath:
            sales = sales_xpath[0].replace('销量：', '')
            data['base']['sales'] = sales

        collection_volume_xpath = html.xpath("//ul[@class='detail-amount']/li[2]/text()")
        if collection_volume_xpath:
            collection_volume = collection_volume_xpath[0]
            collection_volume_re = re.search('.*(\d+)', collection_volume)
            if collection_volume_re:
                collection_volume = data['base']['collection_volume']
                data['base']['collection_volume'] = collection_volume

        mall_name_xpath = html.xpath("//h2[@class='shop-title']/text()")
        if mall_name_xpath:
            mall_name = mall_name_xpath[0].replace('\n', '').replace('\r', '').replace(' ', '')
            data['base']['mall_name'] = mall_name

        imglist2 = []
        imglist_xpath = html.xpath('//*[@class="tb-thumb owl-carousel owl-theme owl-loaded "]//a/img/@src')
        if imglist_xpath:
            for img_i in imglist_xpath:
                imgUrl = img_i if 'https:' in img_i else 'https:' + str(img_i)
                imgUrl = imgUrl.replace('_60x60.jpg', '').replace('_40x40.jpg', '')
                img_i_data = {
                    "type": 0,
                    "imgUrl": imgUrl
                }
                imglist2.append(img_i_data)

        elif imglist_xpath == None:
            imglist_xpath = html.xpath('//*[@id="thumblist"]/div[1]/div/div[1]/div/a/img/@src')
            for img_i in imglist_xpath:
                imgUrl = img_i if 'https:' in img_i else 'https:' + str(img_i)
                imgUrl = imgUrl.replace('_60x60.jpg', '').replace('_40x40.jpg', '')
                img_i_data = {
                    "type": 0,
                    "imgUrl": imgUrl
                }
                imglist2.append(img_i_data)

        info2 = []
        info_xpath = html.xpath('//*[@id="main-con"]/div/div[2]/div[2]/div/div[1]/div[1]/ul/li/@title')  # 一些列表属
        if info_xpath:
            for attr_data in info_xpath[0]:
                attr_data_i = attr_data.split(':')
                data_i = {
                    "productId": str(itemid),
                    "pkey": attr_data_i[0],
                    "pval": attr_data_i[1],
                    "unit": ""
                }
                info2.append(data_i)
        data['attributes'] = info2

        descriptionText = ""
        descriptionText_xpath = html.xpath("//ul[@class='attrs']")
        if descriptionText_xpath:
            descriptionText = etree.tostring(descriptionText_xpath[0]).decode()
            data['extension']['descriptionText'] = descriptionText

        description_re = re.findall(r'<script type="text/x-handlebars-template" id="descTemplate">(.*?)</script>',
                                    sourceHtml, re.S | re.M)
        if description_re:
            description = description_re[0]
            data['extension']['description'] = descriptionText + description

            des_img_list = get_detillimg(description)  # 描述图
            for img_i in des_img_list:
                img_i_data = {
                    "type": 1,
                    "imgUrl": img_i.replace('\\', '') if 'https:' in img_i else 'https:' + str(img_i).replace('\\', '')
                }
                imglist2.append(img_i_data)

        data['images'] = imglist2

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
