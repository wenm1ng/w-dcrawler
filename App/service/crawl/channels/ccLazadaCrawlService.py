# -*- coding: UTF-8 -*-
'''
@Project: dcrawler
@File: ccLazadaCrawlService.py
@Notes: 
@Author: zhuyoucheng
@Date: 2021/3/12 0012 15:25
'''
# coding: utf-8

import re, os, json
import hashlib
from urllib import parse
from App.common.webRequest import WebRequest
from App.model.system.proxyPool.redis.proxyPoolRedis import proxyPoolRedis
from App.service.system.logService import logService
from App.model.crawl.channels.cc1688CrawlRedis import cc1688CrawlRedis
from Configs import defaultApp
from App.service.system.classContextService import classContextService
import json, gevent
from scrapy.selector import Selector
from urllib.parse import urlparse

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class ccLazadaCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
     # 获取数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:58:59
    """

    def appendCurlRequest(self):
        classContextServiceClass = classContextService()
        # ipPool = []
        proxyFreeCNIpPortList = classContextServiceClass.getVarByName(name=self.relayServiceClass.__class__.__name__ + '_proxyFreeCNIpPortList')
        urls = classContextServiceClass.getVarByName(name=self.relayServiceClass.__class__.__name__ + '_urls')
        # if proxyFreeCNIpPortList:
        #     ipPool.extend(proxyFreeCNIpPortList)
        # proxyCNPortList = classContextServiceClass.getVarByName(name=self.relayServiceClass.__class__.__name__ + '_proxyCNPortList')
        # if proxyCNPortList:
        #     ipPool.extend(proxyCNPortList)

        # if self.urls:
        #     for url in self.urls:
        #         for iphost in self.relayServiceClass.proxyFreeCNIpPortList:
        #             self.httpTask.append(gevent.spawn(self.saveHtmlResult, self=self, iphost=iphost, url=url))
        #
        # self.execHttpTak(self=self)

        # result = open('center_amz_listing_3233.html', encoding='utf-8')
        # return self.setResult(self=self, sourceHtml=result.read(), url='https://detail.1688.com/offer/538536532243.html')
        # again

        if urls:
            if 'Lazada' not in urls.keys():
                return
            for url in urls['Lazada']:
                if url not in urls['Lazada']:
                    continue
                # 设置扩展键值
                mainUrlExtendUrls = self.relayServiceClass.getMainUrlExtendUrl(mainUrl=urls['Lazada'][url])
                if not mainUrlExtendUrls:
                    self.relayServiceClass.setMainUrlExtendUrl(mainUrl=urls['Lazada'][url])
                if self.relayServiceClass.isExistsFileNameByUrl(url=urls['Lazada'][url]):
                    htmlFileResult = os.path.isfile(self.relayServiceClass.getFileNameByUrl(url=urls['Lazada'][url]))
                    # htmlFileResult = open(self.relayServiceClass.getFileNameByUrl(url=urls['1688'][url]), encoding='utf-8')
                    if htmlFileResult:
                        with open(self.relayServiceClass.getFileNameByUrl(url=urls['Lazada'][url]), encoding='UTF-8') as file1:
                            file1.seek(0)
                            contents = file1.read()
                            self.setResult(self, contents, urls['Lazada'][url])
                        continue

                self.saveHtmlResult(self=self, url=urls['Lazada'][url])

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
        parse = urlparse(url)
        parseNetloc = 'www.lazada.com.my'
        parsePath = ''
        if parse:
            parseNetloc = str(parse.netloc)
            parsePath = str(parse.path)

        header = {
            'Authority': parseNetloc,
            'Path': parsePath,
            'method': 'GET',
            'scheme': 'https',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            # 'Cookie': '_uab_collina=160775891033030647351532; cna=MilbGEYJX2QCAS9rVY1Rvi/N; UM_distinctid=17655e626ab4d6-0010eee1158fcc-c791039-1fa400-17655e626ac9db; taklid=0e44eec3fed84db186d450598cc48c41; cookie2=113aa6f5327a11ee97a1e53b0d30dbde; t=1005c1682a791cc067f0abbf3f13bfa8; _tb_token_=ee51eb5d5e3fd; xlly_s=1; _m_h5_tk=752c4770e98fb0dbae19687f8b14e690_1608038608013; _m_h5_tk_enc=a2b8b5b47896927287ed8e852fdefa74; lid=%E5%94%AF%E7%88%B1%E4%BD%A0_nsj; ali_apache_track=c_mid=b2b-4293795368a374d|c_lid=%E5%94%AF%E7%88%B1%E4%BD%A0_nsj|c_ms=1|c_mt=3; ali_apache_tracktmp=c_w_signed=Y; last_mid=b2b-4293795368a374d; CNZZDATA1253659577=954988728-1607758317-https%253A%252F%252Fdetail.1688.com%252F%7C1608033021; _is_show_loginId_change_block_=b2b-4293795368a374d_false; _show_force_unbind_div_=b2b-4293795368a374d_false; _show_sys_unbind_div_=b2b-4293795368a374d_false; _show_user_unbind_div_=b2b-4293795368a374d_false; __rn_alert__=false; alicnweb=touch_tb_at%3D1608034303604%7ChomeIdttS%3D82275062466567210651994194792170869619%7ChomeIdttSAction%3Dtrue%7Clastlogonid%3D%25E5%2594%25AF%25E7%2588%25B1%25E4%25BD%25A0_nsj; cookie1=UUBb0lE3SfPz39x3jLuqSu9f33APcSjcbV5HvTBMplE%3D; cookie17=Vy6xzT2X0Wxc4Q%3D%3D; sg=j82; csg=eb814da2; unb=4293795368; uc4=nk4=0%40r8C%2B%2B81RI2zkYR04heAJg4Cu0AK%2F&id4=0%40VXkWSvzFADd%2FtZaKPupSSqPYeUiu; __cn_logon__=true; __cn_logon_id__=%E5%94%AF%E7%88%B1%E4%BD%A0_nsj; _nk_=%5Cu552F%5Cu7231%5Cu4F60_nsj; _csrf_token=1608034613610; ali_ab=47.107.85.141.1608034623562.4; ad_prefer="2020/12/15 20:22:38"; h_keys="%u767e%u8d27"; JSESSIONID=320875A6800D47C71A2E90C48FB612D3; tfstk=c041BwMrCdv1G8j2751EgscXaCica-RSGGMg1lXyugTDKLNnpsqezYsmkovvJ0hC.; l=eBjMndVmO0I7Bbc2BOfZourza77TSIRAguPzaNbMiOCPOF6e5GsAWZJTPWKwCnGVhsQDR3uKcXmBBeYBqHtInxvTZ73Kgjkmn; isg=BHNzM37dKMIcreSaYX47quSCAnedqAdqgCGnlCUQwxLJJJPGrX5LutK82lTKhF9i',#登陆的cookie
            # 'Cookie': 'DG_IID=242F1CF2-30B8-3C60-A56B-76BEAACFF5FD; DG_UID=3266585A-0E85-3D83-9050-C644CE659404; DG_ZID=E5B431B7-F54F-3FB2-AE70-9A22E714E573; DG_ZUID=8BE0352F-F144-3D2D-8242-A504A57B7C55; DG_HID=FE05B9CF-0DB0-38B4-8100-015466D069D0; DG_SID=113.88.14.181:ID9rptzN6D+xOxqk+0DbC7Yx04HH1z+CY/1GVXoWCV0; cid=ELXSfs1t7Z967Ig1%232023822926; __ssds=2; __ssuzjsr2=a9be0cd8e; __uzmaj2=338152b4-d10c-4bbb-bc54-ca0f37f5b51e; __uzmbj2=1610009404; __uzmcj2=558631071698; __uzmdj2=1610009404; ak_bmsc=3EFBF81927EC71B970DA25B833E682F517215E9FBE740000846DFE5F5456D31B~plktdXocOyKE5yoZlyh7j4GdQjJLHlTqGEBGWeXSswASKXvUOr0A17P+R2nRse9qVLZirWs7ybzaoIlrQIvUQqan9p7+dZ7MGgYFb3Ns3SvcoUD23hAmNwJ5Vj5anznC/SzgvCcZaf2W9hznVPup43Z3li72NejOUDvZEiPPse4eYmZU2UI5KPAwr9dV/FQV+mbWYktexA/3pzRH3nE1wIo10AKzvEaZ7UY36FTNvYJZA=; __gads=ID=cd23f59eb71faca9:T=1610509808:S=ALNI_MZfECsAyDK6o1U0zehUBU2-4csm9Q; JSESSIONID=63DA399E16E3DFD14B93B1C7D572AB73; ds2=; ebay=%5Esbf%3D%23100000000000%5Ejs%3D1%5E; dp1=bu1p/QEBfX0BAX19AQA**63c0ef9e^bl/CN63c0ef9e^pbf/%232000000e00060000000000000000461dfbc1e^; s=CgAD4ACBf/9oeZGMwOWM4NjkxNzYwYWM2YTgyMWUxOTFmZmZkNzYzNDUA7gAYX//aHjAGaHR0cHM6Ly93d3cuZWJheS5jb20vB7owNno*; nonsession=BAQAAAXb5Cri4AAaAAAgAHGAmFZ4xNjEwNTE2NjM2eDEzMTcwNTM3NDY4NHgweDJOADMABmHfvB41MTgwMDAAywABX/6PpjEAygAgY8DvnmRjMDljODY5MTc2MGFjNmE4MjFlMTkxZmZmZDc2MzQ1UNBM1iU6cKtD33HpVOO535NUd8o*; bm_sv=3494EADB30E07893C38804EF3CF89EC2~oyk1Zqe4YGc22lq0k23UamlRvXKZK1a7jZ0HmRggXOiJdyo/wxErMij7xw5n2gZFsdjxSS36U3gEziCibme6WNbKI55rwnoWu03fR2hfoTkBghNkgQwGrxGWE8yAtYUTXhvDxgVdgXNA0m4J+BJ++Q==; npii=btguid/dc09c8691760ac6a821e191fffd7634563c0ef9e^cguid/f9dbd7051760ac3db760f72cfb62381a63c0ef9e^',
            'Referer': parseNetloc,
            'Content-Type': 'content-type: text/html; charset=utf-8',

        }
        # proxies = {
        #     'http': 'http://{}'.format(iphost),
        #     'https': 'http://{}'.format(iphost)
        # }
        proxies = None
        print('--------------------------statr------------------------')
        for useType in '011122':
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header, timeout=5)
                print('--------------result----------------')
                # print(result.text(self=WebRequest))
                if result:
                    if result.text(self=WebRequest):
                        if self.isTrueHtml(self=self, htmlText=result.text(self=WebRequest), url=url):
                            with open(self.relayServiceClass.getFileNameByUrl(url=url), 'w', encoding='utf8') as f:
                                f.write(result.text(self=WebRequest))
                        return
                else:
                    result = WebRequest.easyGet(self=WebRequest, url=url, header=header,
                                                timeout=2)
                    if result.text(self=WebRequest):
                        self.isTrueHtml(self=self, htmlText=result.text(self=WebRequest), url=url)
                        with open(self.relayServiceClass.getFileNameByUrl(url=url), 'w', encoding='utf8') as f:
                            f.write(result.text(self=WebRequest))
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
        result = False
        if not htmlText:
            return result
        resultTextSelector = Selector(text=htmlText)
        if not resultTextSelector:
            return result
        print("============isTrue==========")
        productTitle = resultTextSelector.xpath('//h1[@class="pdp-mod-product-badge-title"]/text()').extract_first()
        print(productTitle)
        if productTitle:
            # 追加扩展链接
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
        desc_image = ''
        text_selector = Selector(text=sourceHtml)
        print('================================Lazadastart===================================')
        # 产品ID

        product_id = self.encryMd5(self, url)
        # 标题
        title = text_selector.xpath('//h1[@class="pdp-mod-product-badge-title"]/text()').extract_first()
        # 品牌
        brand_data = text_selector.xpath('//div[@class="pdp-product-brand"]/a/text()').extract()
        brand = json.dumps(brand_data)
        # 站点
        site = ''
        # 币种
        currency_bt = ''
        # 价格
        price = text_selector.xpath('//div[@class="pdp-product-price"]/span/text()').extract_first()
        if price:
            price = price.replace('RM','')

        # 站点语言
        site_language = ''
        # 主图
        main_image_data = text_selector.xpath('//div[@class="item-gallery__image-wrapper"]/img[@class="pdp-mod-common-image item-gallery__thumbnail-image"]/@src').extract()

        main_image = ''
        image_len = len(main_image_data)
        if image_len > 0:
            main_image = main_image_data[0].replace('120x120', '400x400')
        # 橱窗图
        small_image = text_selector.xpath('//div[@class="item-gallery__image-wrapper"]/img[@class="pdp-mod-common-image item-gallery__thumbnail-image"]/@src').extract()
        image_list = []
        for li_xp in small_image:
            if li_xp:
                image_list.append(li_xp)
        small_image = '8-8=,=8-8'.join(image_list)

        # 图文描述
        description_html = re.findall('"@type":"Product","description":"(.*?),"mpn"', sourceHtml)

        if description_html:
            description_html = description_html[0]
            description_html = json.dumps(description_html).replace('\\', '')

        if description_html:
            desc_image = re.findall('src="(.*?)"', description_html)
            desc_image_list = []
            for d_image in desc_image:
                if d_image:
                    desc_image_list.append(d_image)
            desc_image = '8-8=,=8-8'.join(desc_image_list)
        # 简短描述
        description_text = ''
        # 变体
        variation = re.findall('"skuInfos":(.*?),"Breadcrumb"', sourceHtml)
        dict_variation = []
        print('-------------variation---------------')
        if variation:
            dict_variation = json.loads(variation[0])
            if "0" in dict_variation:
                print('del')
                del dict_variation["0"]
        # 变体ID
        var_product_id = ''
        # 变体标题
        var_title = ''
        # 变体图片
        var_image = ''
        # 变体价格
        var_price = ''
        # 变体属性
        var_info = []
        # 变体价格波动
        var_price_range = ''
        variable_list = []

        # 拿到info数据
        sku_info = {}
        sku_base = re.findall('"skuBase":(.*?)},"skuGalleries"', sourceHtml)
        if sku_base:
            sku_base = json.loads(sku_base[0])
            if "properties" in sku_base:
                for v_info in sku_base["properties"]:
                    if v_info["values"]:
                        if not v_info['needLabel']:
                            for v_key,v_info_values in enumerate(v_info["values"]):
                                sku_info_name = v_info_values["vid"]
                                sku_info_value = v_info_values["name"]
                                sku_key = str(v_info["pid"]) + ':' + str(sku_info_name)
                                sku_info[sku_key] = sku_info_value

        for v_value in dict_variation:
            # print(dict_variation[v_key])
            # 变体ID
            var_product_id = dict_variation[v_value]['dataLayer']['pdt_simplesku']
            # 变体标题
            var_title = dict_variation[v_value]['dataLayer']['pdt_name']
            # 变体图片
            var_image = dict_variation[v_value]['image']
            # 变体价格
            var_price = dict_variation[v_value]['price']['salePrice']['value']
            # 库存
            # var_stock = dict_variation[v_key]['stock']

            # info 属性 路径 propPath
            prop_path = ''
            if "skus" in sku_base:
                for skus in sku_base["skus"]:
                    if str(skus["cartSkuId"]) == str(var_product_id):
                        if skus.get("propPath"):
                            prop_path = skus["propPath"]
                            prop_path_list = re.split(';', prop_path)
                            if prop_path_list:
                                for var_attr_key, var_attr_value in enumerate(prop_path_list):
                                    if var_attr_value in sku_info:
                                        var_info_value = {
                                            'pkey': sku_base["properties"][var_attr_key]["name"],
                                            'productId': var_product_id,
                                            'pval': sku_info[var_attr_value],
                                            'unit': ''
                                        }
                                        var_info.append(var_info_value)

            result = self.entity(self, var_product_id, var_title, currency_bt, var_price, var_price_range, var_info, var_image)
            variable_list.append(result)

        json_data = {
            "base": {
                "productId": product_id,
                "title": title,
                "brand": brand,
                "sourceUrl": url,
                "site": site,
                "currency": currency_bt,
                "price": price,
                "priceRange": '',
                "siteLanguage": site_language,
                "platform_type": "",
                "stock": "",
            },
            "images": [
                {
                    "type": 0,
                    "imgUrl": main_image,  # 主图
                },
                {
                    "type": 1,
                    "imgUrl": desc_image,  # 描述图
                },
                {
                    "type": 2,
                    "imgUrl": small_image,  # 橱窗图
                },
            ],
            "attributes": [],
            "extension": {
                "bulletPoint": '',
                "description": description_html,
                "descriptionText": description_text,
                "sku": "",
                "fbaSku": "",
                "fnSku": "",
                "asin1": "",
                "asin2": "",
                "asin3": "",
            },
            'is_valid': 1,
            'variableList': variable_list,
            'token': ""

        }

        product_data = {
            'data': {
                'list': [
                    json_data,
                ]
            }
        }

        # print(product_data)
        return product_data

    def entity(self, productId, product_title, currency, price, priceRange, infos, main_image):
        data = {
            "base": {
                "productId": productId,
                "title": product_title,
                "currency": currency,
                "price": price,
                "priceRange": priceRange,
            },

            "attributes": infos,
            "images": [
                {
                    "type": 0,
                    "imgUrl": main_image,
                },
            ]
        }
        return data

    def encryMd5(self, data):
        m = hashlib.md5(data.encode('utf8'))
        res = m.hexdigest()
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
    # 当前url的数据保存至文件
    # @param self
    # @return string
    # @author     foolminx    foolminx@163.com
    # @date    2020-01-21 14:43:25
    """

    def setUrlsResult(self, url, company_code, user_id):
        htmlFileResult = open(self.relayServiceClass.getFileNameByUrl(url=url), encoding='utf-8')
        # htmlFileResult = open('center_amz_listing_3233.html', encoding='utf-8')
        res = self.setResult(self=self, sourceHtml=htmlFileResult.read(), url=url)
        self.relayServiceClass.resultToJsonFile(result=res, url=url, company_code=company_code, user_id=user_id)
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
