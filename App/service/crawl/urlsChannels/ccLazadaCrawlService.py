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
    des_imglist = HTML.xpath("//div/img/@src")
    return des_imglist

class ccLazadaCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Lazada'

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
        try:
            re_url = re.search('https://.*lazada.*/products/.*-i(\d+)-s(\d+).html?.*', url)
            itemid = re_url.group(1)
            skuid = re_url.group(2)
        except:
            re_url = re.search('https://.*lazada.*/products/i(\d+).html?.*', url)
            if re_url:
                itemid = re_url.group(1)
                skuid = ''
            else:
                re_url = re.search('https://.*lazada.*/products/.*i(\d+)-s(\d+).html?.*', url)
                itemid = re_url.group(1)
                skuid = re_url.group(2)
        site = baseUrlHandle(url).getPlatformAndSite()['site']
        itemid = itemid
        skuid = skuid

        md5str = hashlib.md5('{}{}{}'.format(itemid, skuid, site).encode(encoding='UTF-8')).hexdigest()
        itemid_validity = commonRedisClass.zscoreValByKey('lazada_{}_info'.format(site), '{}'.format(md5str))
        now_time = time.time()
        if itemid_validity != None:
            print('有缓存')
            shijiancha = int(now_time - itemid_validity)
            if shijiancha >= defaultApp.shopee_life_time['info']:
                print('已过期')
            else:
                print('没过期')
                print('http://47.107.142.65:9200/lazada_{site}_info/_doc/{itemid}'.format(site=site, itemid=md5str))
                data = commonElasticSearchClass.getSourceByIndexKey(index='lazada_{}_info'.format(site), doc_type="_doc", id=md5str)
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                return

        header = {}
        for useType in '0111222':
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            header['User-Agent'] = userAgent().getPc()

            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header, timeout=5)
                data = self.setResult(result.text(self=WebRequest), url)  # 洗完的结构
                print(666, data)
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                commonElasticSearchClass.insertDataByIndexKey(index='lazada_{}_info'.format(site), id=md5str, data=data)
                commonRedisClass.insertDataByIndexKey(redisKeyName='lazada_{}_info'.format(site), redisStr=md5str)
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
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """

    def setResult(self,sourceHtml,url):
        print(url)
        data = {
            'extra_data': [],
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
                "quantity": "",
                "mall_id": "",
                "mall_link": "",
                "mall_name": "",

                "front_desk_type": "",  # 前台分类
                "size": '',  # 尺寸
                "weight_value": '',  # 重量值
                "weight_unit": ''  # 重量单位
            },
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
        # praise_rate 好评率
        praise_rate = html.xpath('//div[@class="seller-info-value rating-positive "]/text()')
        if praise_rate:
            data['base']['praise_rate'] = praise_rate[0]
        # goods_deliver 发货
        goods_deliver = html.xpath('//div[@class="seller-info-value "]/text()')
        if goods_deliver:
            data['base']['goods_deliver'] = goods_deliver[0]
        # response 响应
        response = html.xpath('//div[@class="seller-info-value "]/text()')
        if response:
            data['base']['response'] = response[-1]

        sourceHtml_re = re.search(r'var __moduleData__ = ({.*?."module_popups".}}});', sourceHtml)
        if sourceHtml_re == None:
            return
        sourceHtml = sourceHtml_re.group(1)  ## xxx.group(0)原字符串 xxx.group(1)实际匹配的
        sourceHtml_dict = json.loads(sourceHtml)

        sourceHtml_dict = {'data': {'root': {'fields': sourceHtml_dict['data']['root']['fields']}}}

        itemid = sourceHtml_dict['data']['root']['fields']['primaryKey']['itemId']
        data['base']['productId'] = itemid

        title = sourceHtml_dict['data']['root']['fields']['product']['title']
        data['base']['title'] = title

        brand = sourceHtml_dict['data']['root']['fields']['product']['brand']['name']
        data['base']['brand'] = brand

        site = sourceHtml_dict['data']['root']['fields']['globalConfig']['site']
        data['base']['site'] = site

        price = sourceHtml_dict['data']['root']['fields']['skuInfos']['0']['price']['salePrice']['value']
        data['base']['price'] = price

        mall_id = sourceHtml_dict['data']['root']['fields']['seller']['shopId']
        data['base']['mall_id'] = mall_id

        mall_link  = sourceHtml_dict['data']['root']['fields']['seller']['url']
        data['base']['mall_link'] = mall_link

        mall_name = sourceHtml_dict['data']['root']['fields']['seller']['name']
        data['base']['mall_name'] = mall_name

        product_rating = sourceHtml_dict['data']['root']['fields']['product']['rating']['score']
        data['base']['product_rating'] = product_rating

        comments_number = sourceHtml_dict['data']['root']['fields']['product']['rating']['total']
        data['base']['comments_number'] = comments_number

        currency = sourceHtml_dict['data']['root']['fields']['globalConfig']['currency']
        data['base']['currency'] = currency

        # front_desk_type
        front_desk_types = sourceHtml_dict['data']['root']['fields']['skuInfos']['0']['dataLayer']['pdt_category']
        if front_desk_types:
            front_desk_type_lsit = []
            for category in front_desk_types:
                front_desk_type_lsit.append(category)
            data['base']['front_desk_type'] = '>'.join(front_desk_type_lsit)


        imglist2 = []
        for img_i in sourceHtml_dict['data']['root']['fields']['skuGalleries']['0']:
            img_i_data = {
                "type": 0,
                "imgUrl": 'https:' + str(img_i['src'])
            }
            imglist2.append(img_i_data)
        data['images'] = imglist2

        variableList2 = []
        skus = sourceHtml_dict['data']['root']['fields']['skuInfos']
        del skus['0']
        for sku_id_i in sourceHtml_dict['data']['root']['fields']['primaryKey']['loadedSkuIds']:
            variable_data = skus[str(sku_id_i)]
            base_i = {
                "productId": str(sku_id_i),
                "title": str(title),
                "currency": currency,
                "price": variable_data['price']['salePrice']['value'],
                "priceRange": "",
                "stock": variable_data['stock'],
                "sales": 0
            }
            attributes_data = []
            for j in variable_data['operations']:
                attributes_i = {
                    "pkey": j['type'],
                    "productId": int(itemid),
                    "pval": j['text'],
                    "unit": ""
                }
                attributes_data.append(attributes_i)
            images_i = [
                {
                    "type": 3,
                    "imgUrl": 'https:' + variable_data['image']
                }
            ]
            varia_i = {
                "base": base_i,
                "attributes": attributes_data,
                "images": images_i
            }
            variableList2.append(varia_i)
        data['variableList'] = variableList2

        try:
            ee = sourceHtml_dict['data']['root']['fields']['product']['highlights']
            size = re.findall('Size:(.*?)</li>', str(ee))
            if size:
                data['base']['size'] = size[0]
            weight = re.findall('Weight:(.*?)</li>', str(ee))
            if weight:
                data['base']['weight_value'] = weight[0]
        except KeyError:
            ee = ''
        try:
            rr = sourceHtml_dict['data']['root']['fields']['product']['desc']
            detillimg = get_detillimg(rr)
            size = re.findall('Size:(.*?)<br/>',str(rr))
            if size:
                data['base']['size'] = size[0]
            weight = re.findall('Weight:(.*?)<br/>',str(rr))
            if weight:
                data['base']['weight_value'] = weight[0]
            for img_i in detillimg:
                img_i_data = {
                    "type": 1,
                    "imgUrl": str(img_i)
                }
                imglist2.append(img_i_data)
        except KeyError:
            rr = ''
        description = ee+rr
        data['extension']['description'] = description
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


