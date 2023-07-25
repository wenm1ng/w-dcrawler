# coding: utf-8

import re, os, json
import hashlib
from App.common.webRequest import WebRequest
from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis
from App.service.system.logService import logService
from App.model.crawl.channels.cc1688CrawlRedis import cc1688CrawlRedis
from App.service.system.classContextService import classContextService
import json, gevent
from scrapy.selector import Selector
from Configs import defaultApp
from urllib.parse import urlparse

from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent

import hashlib
import requests
import datetime,time

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class ccEbayCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Ebay'

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
     # 获取扩展数据
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
        md5str = None
        # reSearchitmD = re.search('https://www.ebay.com/itm/.*?/(\d+).*?', url)
        reSearchitmD = re.search('(\d+).*?(\d+).*', url)
        if reSearchitmD:
            itemid = reSearchitmD.group(1)
            if itemid:
                md5str = hashlib.md5(itemid.encode(encoding='UTF-8')).hexdigest()

        itemid_validity = commonRedisClass.zscoreValByKey('ebay_info', '{}'.format(md5str))
        now_time = time.time()
        # if itemid_validity != None:
        #     print('有缓存')
        #     shijiancha = int(now_time - itemid_validity)
        #     if shijiancha >= defaultApp.ebay_life_time['info']:
        #         print('已过期')
        #     else:
        #         print('没过期')
        #         print('http://47.107.142.65:9200/ebay_info/_doc/{itemid}'.format(itemid=md5str))
        #         data = commonElasticSearchClass.getSourceByIndexKey(index='ebay_info', doc_type="_doc", id=md5str)
        #         self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
        #         self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
        #         return

        header = {}
        for useType in '01122':

            header['USETYPE'] = useType
            header['TARGETURL'] = url
            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header, timeout=8)
                # if self.isTrueHtml(result.text(self=WebRequest), url):
                html = result.text(self=WebRequest)
                print(len(html))
                if html and len(html)>3000:
                    data = self.setResult(html, url)  # 洗完的结构
                    # print(666, json.loads(data))
                    self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                    commonElasticSearchClass.insertDataByIndexKey(index='ebay_info', id=md5str, data=data)
                    commonRedisClass.insertDataByIndexKey(redisKeyName='ebay_info', redisStr=md5str)
                    self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                    return
                else:
                    continue
            except Exception as e:
                print('error:',e)

    """
     # 判断是否为真实连接
     # @param self
     # @param htmlText 抓取页面
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月20日 16:19:15
    """

    def isTrueHtml(self, htmlText, url):
        result = False
        if not htmlText:
            return result
        resultTextSelector = Selector(text=htmlText)
        if not resultTextSelector:
            return result
        productTitle = resultTextSelector.xpath('//h1[@id="itemTitle"]/text()').extract_first()
        if productTitle:
            return True
        else:
            return False

    """
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """

    def setResult(self, sourceHtml, url):
        mainImage = ''
        # productId
        print('--------------------------setResult---------------------------------')
        product_id_temp = re.findall(r'/(\d+)\?', url)
        product_id = product_id_temp[0] if product_id_temp else None
        if not product_id:
            product_id_temp = re.findall(r'/(\d+)', url)
            product_id = product_id_temp[0] if product_id_temp else None
        # 站点
        site = self.siteConfig2(re.search('www\.(.*?)/', url).group(1))
        # print('-----------------------site-----------------------')
        # print(site)
        resultTextSelector = Selector(text=sourceHtml)
        # 标题
        productTitle = resultTextSelector.xpath('//h1[@id="itemTitle"]/text() | //h1[@class="product-title"]/text()').extract()
        # state = resultTextSelector.xpath('//div[@id="vi-itm-cond"]/text()').extract()

        productTitle = ''.join(productTitle)
        # 品牌
        brand = resultTextSelector.xpath('//a[@id="bylineInfo"]//text()|//h2[@itemprop="brand"]/span/text()').extract_first()
        # 平台语言
        siteLanguage = resultTextSelector.xpath('//a/@data-language').extract_first()
        # 主图
        # mainImage = resultTextSelector.xpath('//img[@itemprop="image"]/@src').extract_first()
        # 币种
        currency = resultTextSelector.xpath('//span[@itemprop="priceCurrency"]/@content').extract_first()
        if not currency:
            currency_re = re.findall('priceCurrency":"(.*?)"', sourceHtml)
            if currency_re:
                currency = currency_re[0]
            else:
                currency = 'USD'
        # 价格
        price = ''
        price_text = resultTextSelector.xpath('//span[@itemprop="price"]/@content').extract_first()
        if price_text:
            price = re.search('\d(.*)', price_text).group()
        if not price:
            prices = re.findall('"price":"(.*?)"', sourceHtml)
            if prices:
                price = prices[0]
        # 完整html
        # descriptionHtml = resultTextSelector.xpath('//div[@class="tabbable"]//div[@id="desc_wrapper_ctr"]').extract_first()
        descriptionHtml_url = resultTextSelector.xpath('//div[@id="desc_wrapper_ctr"]/div/iframe/@src').extract_first()
        if not descriptionHtml_url:
            descriptionHtml_url = resultTextSelector.xpath(
                '//iframe[@id="desc_ifr"]/@src').extract_first()
        # print('descriptionHtml_url:',descriptionHtml_url)
        if descriptionHtml_url:
            descriptionHtml = self.get_detail(descriptionHtml_url)
        else:
            descriptionHtml = ''
        # 选段html
        # partDescriptionHtml = resultTextSelector.xpath('//div[@class="section"]/table/tr|//div[@class="vi-desc-revHistory"]').extract_first()
        # 库存
        quantitys = resultTextSelector.xpath('//span[@id="qtySubTxt"]/span/text()').extract_first()
        stock = ''
        if quantitys:
            quantity_re = re.findall('\d+',str(quantitys).replace(' ','').strip())
            stock = [quantity_re[0] if quantity_re else ''][0]
        else:
            quantitys = resultTextSelector.xpath('//select[@class="listbox__control listbox__control--fluid vi-quantity__select-box"]/option/@value').extract()
            if quantitys:
                stock = quantitys[-1]

        if not stock:
            stock = resultTextSelector.xpath('//input[@id="qtyTextBox"]/@value').extract_first()

        if not stock:
            stock = ''
        # 销量
        sales_xp = resultTextSelector.xpath('//a[@class="vi-txt-underline"]/text()').extract_first()
        if not sales_xp:
            sales_xp = resultTextSelector.xpath('//div[@class="banner-status"]/text()').extract_first()
        if sales_xp:
            sales_re = re.findall('\d+',str(sales_xp))
            if sales_re:
                sales = sales_re[0]
            else:
                sales = ''
        else:
            sales = ''
        # 新增
        # front_desk_type前台分类
        front_desk_types = resultTextSelector.xpath('//li[@id="vi-VR-brumb-lnkLst"]/ul/li[@class="bc-w"]')
        front_desk_list = []

        for li in front_desk_types:
            # front_desk = li.xpath('./a/span/text()').extract_first()
            front_ids = li.xpath('./a/@href').extract_first()
            front_id = str(front_ids).split('/')[-1] if front_ids else ''
            front_desk_list.append(front_id)
        front_desk_type = front_desk_list[-1] if front_desk_list else ''
        weight = ''
        size = ''
        weight_value = ''
        weight_unit = ''
        table = resultTextSelector.xpath('//div[@class="section"]//tr | //section[@class="product-spectification"]//li')
        descriptionTextlist = []
        for item in table:
            td1 = item.xpath('./td[@class="attrLabels"][1]/text() | ./div[@class="s-name"]/text()').extract_first()
            if td1:
                td1 = td1.replace(' ', '').strip()
            td2 = item.xpath('./td[@class="attrLabels"][2]/text()').extract_first()
            if td2:
                td2 = td2.replace(' ', '').strip()
            th1 = item.xpath('./td[@width="50.0%"][1]//span/text() | ./div[@class="s-value"]/text()').extract_first()
            th2 = item.xpath('./td[@width="50.0%"][2]//span/text()').extract_first()
            if 'Brand' in str(td1) or '品牌' in str(td1):
                if not brand:
                    brand = th1
            elif 'Brand' in str(td2) or '品牌' in str(td2):
                if not brand:
                    brand = th2
            if 'Weight' in str(td1) or '重量' in str(td1):
                weight = th1
            elif 'Weight' in str(td2) or '重量' in str(td2):
                weight = th2
            if 'Dimensions:' in str(td1) or 'dimensions' in str(td1) or '尺寸' in str(td1):
                size = th1
            elif 'Dimensions:' in str(td2) or 'dimensions' in str(td2) or '尺寸' in str(td2):
                size = th2

            infostr1 = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=str(td1).replace(':', ''), value=th1)
            descriptionTextlist.append(infostr1)
            if td2:
                infostr2 = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=str(td2).replace(':', ''),
                                                                                   value=th2)
                descriptionTextlist.append(infostr2)

        partDescriptionHtml = ''.join(descriptionTextlist)
        if weight and ' ' in weight:
            weight_value = str(weight).split(' ')[0]
            weight_unit = str(weight).split(' ')[1]
        elif len(weight) > 1:
            weight_re = re.findall('\d+.?\d+', str(weight))
            if weight_re:
                weight_value = weight_re[0]
                weight_unit = weight[len(weight_value):]

        praise_rates = resultTextSelector.xpath('//div[@id="si-fb"]/text()').extract()
        if praise_rates:
            praise_rate = str(praise_rates[0]).split('\xa0')[0]
        else:
            praise_rate = ''

        comments_number = resultTextSelector.xpath('//a[@class="see--all--reviews-link"]/text()').extract_first()

        credit_score = resultTextSelector.xpath('//span[@class="mbg-l"]/a/text()').extract_first()
        merchants = resultTextSelector.xpath('//span[@class="mbg-nw"]/text()').extract_first()
        # 小图
        small_image_xp = resultTextSelector.xpath('//div[@id="vi_main_img_fs"]/ul/li | //div[@class="thumbPicturePanel "]//span')
        image_list = []

        for i,li_xp in enumerate(small_image_xp):
            img = li_xp.xpath('.//img/@src').extract_first()
            if img:
                imageSearch = re.search('s-(.*?).(jpg|png)', img)
                if imageSearch:
                    if imageSearch.group(1):
                        img_number = imageSearch.group(1)
                        big_img = img.replace(img_number, 'l500')
                        if i == 0:
                            img_i_data = {
                                "type": 0,
                                "imgUrl": big_img
                            }
                        else:
                            img_i_data = {
                                "type": 2,
                                "imgUrl": big_img
                            }
                        image_list.append(img_i_data)
                else:
                    img_i_data = {
                        "type": 2,
                        "imgUrl": img
                    }
                    image_list.append(img_i_data)

        if len(image_list)<1:
            image_item = resultTextSelector.xpath('//div[@id="mainImgHldr"]/img[@id="icImg"]/@src').extract()
            if image_item:
                img_i_data = {
                    "type": 0,
                    "imgUrl": image_item[0]
                }
                image_list.append(img_i_data)

        # print('image_list:',len(image_list))

        variant_res = re.search('"menuItemMap":(.*?),"menuItemPictureIndexMap', sourceHtml)

        variant_html = variant_res.group(1) if variant_res else ''
        try:
            variant_dic = json.loads(variant_html) if variant_html else ''
        except:
            variant_res = re.search('"menuItemMap":(.*?}}),"', sourceHtml)
            variant_html = variant_res.group(1) if variant_res else ''
            variant_dic = json.loads(variant_html) if variant_html else ''
        variant_gx = {}
        if variant_dic:
            for vd in variant_dic.values():
                variant_name = vd['valueName']
                variant_id = vd['valueId']
                variant_gx[variant_id] = variant_name

        # 获取关系映射--变体
        itemVariations_map = re.search('"itemVariationsMap":(.*?),"unavailableVariationIds"', sourceHtml)
        itemVariations_html = itemVariations_map.group(1) if itemVariations_map else ''
        if not itemVariations_html:
            patten = re.compile('"itemVariationsMap":(.*?)"unavailableVariationIds"', re.DOTALL)
            itemVariations_map = re.search(patten, sourceHtml)
            itemVariations_htmls = itemVariations_map.group(1) if itemVariations_map else ''
            itemVariations_html = str(itemVariations_htmls).strip()[:-1]

        try:
            itemVariations_dic = json.loads(itemVariations_html) if itemVariations_html else ''
        except:
            itemVariations_map = re.search('"itemVariationsMap":(.*false}}),"', sourceHtml)
            itemVariations_html = itemVariations_map.group(1) if itemVariations_map else ''
            itemVariations_dic = json.loads(itemVariations_html) if itemVariations_html else ''
        variableList = []
        priceRange_list = []
        priceRange = ''
        # print("变体内容：",itemVariations_dic)
        if itemVariations_dic:
            for id, id_value in itemVariations_dic.items():
                product_id = id
                if 'priceAmountValue' in id_value:
                    priceAmountValue = id_value['priceAmountValue']
                    if 'convertedFromCurrency' in priceAmountValue:
                        currency_bt = priceAmountValue['convertedFromCurrency']
                    elif 'currency' in priceAmountValue:
                        currency_bt = priceAmountValue['currency']
                    else:
                        currency_bt = ''
                else:
                    currency_bt = ''
                id_price = id_value['price']
                id_price = self.get_amz_price(id_price)
                priceRange_list.append(float(id_price))
                traitValuesMap = id_value['traitValuesMap']
                infos = []

                for t in traitValuesMap:
                    variant_val = variant_gx[traitValuesMap[t]]
                    pj_data = {
                        'pkey': t,
                        'productId': product_id,
                        'pval': variant_val,
                        'unit': ''
                    }
                    infos.append(pj_data)
                img_list = []
                for img in image_list:
                    img_i_dict = {
                        "type": 2,
                        "imgUrl": img['imgUrl']
                    }
                    img_list.append(img_i_dict)
                result = self.entity(product_id, productTitle, currency_bt, id_price, priceRange, infos, img_list, stock)
                variableList.append(result)


        # baseSourceUrl = resultTextSelector.xpath("//link[@rel='canonical']/@href").extract_first()
        baseSourceUrl = url
        if priceRange_list:
            priceRange = str(min(priceRange_list)) + '~' + str(max(priceRange_list))
        if not priceRange:
            priceRange = price
        json_data = {
            "base": {
                "productId": product_id,
                "title": productTitle,
                "brand": brand,
                "sourceUrl": baseSourceUrl,
                "site": site,
                "currency": currency,
                "price": price,
                "priceRange": priceRange,
                "siteLanguage": siteLanguage,
                "platform_type": "",
                "stock": stock, # 库存
                'sales': sales,  # 销量
                # 新增
                "size":size,
                "weight_value":weight_value,
                "weight_unit":weight_unit,
                "praise_rate":praise_rate, # 商品评分
                "comments_number":comments_number, # 评论数量
                "front_desk_type":front_desk_type,  # 前台分类
                "credit_score":credit_score,  # 信用分
                "merchants": merchants  # 联系卖家
            },
            "images": image_list,
            "attributes": [],
            "extension": {
                "bulletPoint": '',
                "description": descriptionHtml,
                "descriptionText": partDescriptionHtml,
                "sku": "",
                "fbaSku": "",
                "fnSku": "",
                "asin1": "",
                "asin2": "",
                "asin3": "",
            },
            'is_valid': 1,
            'variableList': variableList,
            'token': ""

        }
        # print(json_data)
        return json_data

    def entity(self, productId, product_title, currency, price, priceRange, infos, img_list,stock):
        data = {
            "base": {
                "productId": productId,
                "title": product_title,
                "currency": currency,
                "price": price,
                "stock": stock,
                "priceRange": priceRange,
            },

            "attributes": infos,
            "images": img_list
        }
        return data


    def encryMd5(self, data):
        m = hashlib.md5(data)
        res = m.hexdigest()
        # print(res)
        return res

    def get_amz_price(self, source_price):
        if source_price:
            res = re.findall('([^0-9.,]*)([0-9.,]*)([^0-9.,]*)', source_price)
            price = res[0][1]
        else:
            price = ''
        return price

    def resetClassVar(self):
        self.proxyIpPortList = []

    pass

    """
    # 设置站点
    """

    def siteConfig(self, site):
        # [16] = > "https://www.ebay.at/"
        # [15] = > "https://www.ebay.com.au/"
        # [193] = > "https://www.ebay.ch/"
        # [77] = > "https://www.ebay.de/"
        # [2] = > "https://www.ebay.ca/"
        # [186] = > "https://www.ebay.es/"
        # [71] = > "https://www.ebay.fr/"
        # [23] = > "https://www.befr.ebay.be/"
        # [210] = > "https://www.cafr.ebay.ca/"
        # [3] = > "https://www.ebay.co.uk/"
        # [201] = > "https://www.ebay.com.hk/"
        # [205] = > "https://www.ebay.ie/"
        # [203] = > "https://www.ebay.in/"
        # [101] = > "https://www.ebay.it/"
        # [100分] = > "https://www.ebay.com/"
        # [207] = > "https://www.ebay.com.my/"
        # [146] = > "https://www.ebay.nl/"
        # [123] = > "https://www.benl.ebay.be/"
        # [211] = > "https://www.ebay.ph/"
        # [212] = > "https://www.ebay.pl/"
        # [216] = > "https://www.ebay.com.sg/"
        # [0] = > "https://www.ebay.com/"
        switch = {
            'ebay.at': 16,
            'ebay.com.au': 15,
            'ebay.ch': 193,
            'ebay.de': 77,
            'ebay.ca': 2,
            'ebay.es': 186,
            'ebay.fr': 71,
            'befr.ebay.be': 23,
            'cafr.ebay.ca': 210,
            'ebay.co.uk': 3,
            'ebay.com.hk': 201,
            'ebay.ie': 205,
            'ebay.in': 203,
            'ebay.it': 101,
            'ebay.com.my': 207,
            'ebay.nl': 146,
            'benl.ebay.be': 123,
            'ebay.ph': 211,
            'ebay.pl': 212,
            'ebay.com.sg': 216,
            'ebay.com': 0
        }
        return switch.get(site)

    """
    # 设置站点
    """

    def siteConfig2(self, site):
        # [16] = > "https://www.ebay.at/"
        # [15] = > "https://www.ebay.com.au/"
        # [193] = > "https://www.ebay.ch/"
        # [77] = > "https://www.ebay.de/"
        # [2] = > "https://www.ebay.ca/"
        # [186] = > "https://www.ebay.es/"
        # [71] = > "https://www.ebay.fr/"
        # [23] = > "https://www.befr.ebay.be/"
        # [210] = > "https://www.cafr.ebay.ca/"
        # [3] = > "https://www.ebay.co.uk/"
        # [201] = > "https://www.ebay.com.hk/"
        # [205] = > "https://www.ebay.ie/"
        # [203] = > "https://www.ebay.in/"
        # [101] = > "https://www.ebay.it/"
        # [100分] = > "https://www.ebay.com/"
        # [207] = > "https://www.ebay.com.my/"
        # [146] = > "https://www.ebay.nl/"
        # [123] = > "https://www.benl.ebay.be/"
        # [211] = > "https://www.ebay.ph/"
        # [212] = > "https://www.ebay.pl/"
        # [216] = > "https://www.ebay.com.sg/"
        # [0] = > "https://www.ebay.com/"
        switch_2 = {
            'ebay.at': 'AT',
            'ebay.com.au': 'AU',
            'ebay.ch': 'CH',
            'ebay.de': 'DE',
            'ebay.ca': 'CA',
            'ebay.es': 'ES',
            'ebay.fr': 'FR',
            'befr.ebay.be': 'BE',
            'cafr.ebay.ca': 'CA',
            'ebay.co.uk': 'UK',
            'ebay.com.hk': 'HK',
            'ebay.ie': 'IE',
            'ebay.in': 'IN',
            'ebay.it': 'IT',
            'ebay.com.my': 'MY',
            'ebay.nl': 'NL',
            'benl.ebay.be': 'BE',
            'ebay.ph': 'PH',
            'ebay.pl': 'PL',
            'ebay.com.sg': 'SG',
            'ebay.com': 'US'
        }
        return switch_2.get(site)

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
     # 设置对象
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:56:10
    """

    def setRelayServiceClass(self, relayServiceClass):
        if not relayServiceClass:
            return False
        self.relayServiceClass = relayServiceClass

    def get_detail(self, url):
        header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'Host': 'vi.vipr.ebaydesc.com',
            'upgrade-insecure-requests': '1',
        }
        for useType in '012':
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            header['User-Agent'] = userAgent().getPc()

            try:
                result = WebRequest.easyGet(self=WebRequest, url=url, header=header,
                                            timeout=5)
                html = result.text(self=WebRequest)
                # print('detail_html:',len(html))
                if len(html) > 1000:
                    resultTextSelector = Selector(text=html)
                    descriptionHtml = resultTextSelector.xpath('//div[@class="patemplate_contentin"]').extract_first()
                    if not descriptionHtml:
                        descriptionHtml = resultTextSelector.xpath('//div[@id="container"] | //div[@id="ds_div"]').extract_first()
                    return descriptionHtml
            except Exception as e:
                print('get_detail_error:',e)

