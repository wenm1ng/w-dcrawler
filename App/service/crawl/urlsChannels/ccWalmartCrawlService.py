# -*- coding: utf-8 -*- 
"""
Project: spider
Creator: Eccang
Create time: 2021-06-30 16:31
IDE: PyCharm
Introduction:
"""


import random
import re, os.path, time, urllib.parse

from App.common.webRequest import WebRequest
from Configs import defaultApp
from App.service.system.logService import logService

from App.common.url.baseUrlHandle import baseUrlHandle
import json, gevent

from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent
from urllib.parse import urlparse, parse_qs
from lxml import etree
import hashlib
import requests

class ccWalmartCrawlService(object):
    """
        # 对象
        # @var string
        """
    relayServiceClass = {}
    def setRelayServiceClass(self, relayServiceClass):
        if not relayServiceClass:
            return False
        if not self.relayServiceClass:
            self.relayServiceClass = relayServiceClass

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Walmart'

    """
     # 设置对象
     # @param self
     # @return string
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

        # re_url = re.findall('https://www.walmart.com.*?/(\d+).*?', url)
        # if re_url:
        #     item_id = re_url[0]
        # else:
        #     item_id = baseUrlHandle(url).getPlatformAndSite()['site'].lower()
        site = 'us'#baseUrlHandle(url).getPlatformAndSite()['site'].lower()
        # md5str = hashlib.md5(url.encode(encoding='UTF-8')).hexdigest()
    
        md5str = hashlib.md5(url.encode(encoding='UTF-8')).hexdigest()
        # itemid_validity = commonRedisClass.zscoreValByKey('walmart_{}_info'.format(site), '{}'.format(md5str))
        # now_time = time.time()
        # if itemid_validity != None:
        #     print('有缓存')
        #     shijiancha = int(now_time - itemid_validity)
        #     if shijiancha >= defaultApp.shopee_life_time['info']:
        #         print('已过期')
        #     else:
        #         print('没过期')
        #         print('http://47.107.142.65:9200/walmart_{site}_info/_doc/{itemid}'.format(site=site, itemid=md5str))
        #         data = commonElasticSearchClass.getSourceByIndexKey(index='walmart_{}_info'.format(site),
        #                                                             doc_type="_doc", id=md5str)
        #         self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
        #         self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
        #         return

        header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
        }

        for useType in '01122':
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            header['user-agent'] = userAgent().getPc()
            try:
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                            timeout=5)
                html = result.text(self=WebRequest)
                if html:
                    data = self.setResult(html, site, url)  # 洗完的结构
                    print(666, data)
                    if data['base']['title']:
                        self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                        commonElasticSearchClass.insertDataByIndexKey(index='walmart_{}_info'.format(site), id=md5str, data=data)
                        commonRedisClass.insertDataByIndexKey(redisKeyName='walmart_{}_info'.format(site), redisStr=md5str)
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

        flag = False
        if len(htmlText) > 2000:
            flag = True
        return flag

    """
     # 解析数据
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:59:18
    """

    def setResult(self, sourceHtml, site, url):
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
                "business_years": "",  # 商家年限
                "location": "",  # 地区
                "contact_seller": "",  # 联系卖家

                "sales": "",  # 销量
                "collection_volume": "",  # 收藏量
                "praise_rate": "",  # 好评率
                "product_rating": "",  # 商品评分
                "rating_number": "",  # 评分数量
                "comments_number": "",  # 评论数量
                "stock": "",  # 库存

                "size": "",
                "weight_value": '',  # 重量值
                "weight_unit": '',  # 重量单位
                "phone": '',  # 联系方式
                "categories_bag": '',  # 分类
                "e_mail": ''
            },
            'extra_data': [],
            'images': [],
            'attributes': [],
            'variableList': [],
            'is_valid': '',
            'extra': '',
            'extension': {
                "bulletPoint":"",
                'descriptionText': "",
                'description': ""
            }
        }

        data['base']['sourceUrl'] = url
        data['base']['site'] = site
        var_obj_re = re.search(
            re.compile('<script id="item" class="tb-optimized" type="application/json">(.*?)</script>', re.DOTALL),
            str(sourceHtml))

        if var_obj_re:
            var_obj_re = str(var_obj_re.group()).replace('<script id="item" class="tb-optimized" type="application/json">','').replace('</script>','')
            var_json = json.loads(var_obj_re)
            print('var_obj_re:', json.dumps(var_json))
            productId = re.findall('walmart.*?\/(\d+)|\?', url)
            if productId:
                productId = productId[0]
            else:
                productId = var_json['item']['productId']
            title = var_json['item']['product']['midasContext']['query']
            if var_json['item']['product']['buyBox']['prices']:
                currency = var_json['item']['product']['buyBox']['prices'][0].get('currencyUnitSymbol')
            else:
                currency = ''
            if not currency:
                currency = var_json['item']['product']['buyBox']['products'][0]['priceMap'][
                    'currencyUnitSymbol']  # currencyUnit

            stock = var_json['item']['product'].get('maxQuantity')
            if not stock:
                stock = var_json['item']['product']['buyBox']['products'][0]['maxQuantity']

            price = var_json['item']['product']['midasContext']['price']
            if not price:
                if 'price' in var_json['item']['product']['buyBox']['products'][0]['priceMap']:
                    price = var_json['item']['product']['buyBox']['products'][0]['priceMap']['price']
                elif len(var_json['item']['product']['buyBox']['prices'])==1:
                    price = var_json['item']['product']['buyBox']['prices'][0]['price']

            price_list = []
            priceRanges = var_json['item']['product']['buyBox']['prices']

            min_max_price = {}
            for i, pri in enumerate(priceRanges):
                if 'price' in pri:
                    price_list.append(pri['price'])
                    min_max_price['price_{}'.format(i)] = pri['price']
                elif 'maxPrice' in pri:
                    mi = str(price_list[pri['minPrice']]) + ',' + str(price_list[pri['maxPrice']])
                    min_max_price['price_{}'.format(i)] = mi
            if price_list:
                if min(price_list) != max(price_list):
                    priceRange = str(min(price_list)) + '~' + str(max(price_list))
                elif min(price_list) == max(price_list):
                    priceRange = max(price_list)
            else:
                priceRange = price



            brand = var_json['item']['product']['midasContext']['brand']

            product_rating = var_json['item']['product']['reviews'].get('averageOverallRating')
            praise_rate = var_json['item']['product']['reviews'].get('recommendedPercentage')
            rating_number = var_json['item']['product']['reviews'].get('totalReviewCount')

            # if 'totalCommentsCount' in var_json['item']['product']['checkoutComments']:
            #     comments_number = var_json['item']['product']['checkoutComments'].get('totalCommentsCount')
            # else:
            #     comments_number = ''

            # front_desk_type
            # front_desk_type = var_json['item']['product']['buyBox']['products'][0]['categoryPath']

            # 橱窗图
            index_img_list = []
            images = var_json['item']['product']['buyBox']['products'][0]['images']
            for img in images:
                img_i_data = {
                    "type": 2,
                    "imgUrl": img['url']
                }
                index_img_list.append(img_i_data)

            # 变体图
            if var_json['item']['product']['buyBox'].get('criteria'):
                images_i = var_json['item']['product']['buyBox']['criteria'][0]['values']
                for  img in images_i:
                    if 'swatch' in img:
                        img_i_data = {
                            "type": 3,
                            "name": var_json['item']['product']['buyBox']['criteria'][0]['name'],
                            "value": img['title'],
                            "imgUrl": img['swatch']
                        }
                        index_img_list.append(img_i_data)

            # 简短描述
            info = var_json['item']['product']['buyBox']['products'][0]['idmlSections']['specifications']
            descriptionTextlist = []
            for attr_data in info:
                # attr_data_i = filliter(attr_data.xpath('.//text()'))
                key = attr_data['name']
                value = attr_data['value']
                infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=key, value=value)
                descriptionTextlist.append(infostr)
            descriptionText = ''.join(descriptionTextlist)

            # 五点描述
            bulletPoint_html = var_json['item']['product']['buyBox']['products'][0]['detailedDescription']#['idmlSections']['idmlLongDescription']
            # pat = re.compile('>(.*?)<')
            # bulletPoints = pat.findall(bulletPoint_html)
            # if bulletPoints:
            #     bulletPoints = [str(bull).replace('&nbsp;','') for bull in bulletPoints]
            #     bulletPoint = '8-8=,=8-8'.join(bulletPoints)
            # else:
            #     bulletPoint = ''
            bulletPoint = re.sub(r'<[^>]+>|&nbsp;', '8-8=,=8-8', bulletPoint_html)
            # 图文描述
            html = etree.HTML(sourceHtml)
            desc_xpath = html.xpath('//div[@class="Grid about-product-alt-image-flex-container"]')
            if not descriptionText:
                desc_xpath = html.xpath('//div[@class="about-desc about-product-description xs-margin-top"]')
            if desc_xpath:
                desc1 = etree.tostring(desc_xpath[0]).decode()
                desc1 = desc1.replace('<noscript>', '').replace('</noscript>', '')
                description = desc1.replace('\n', '').replace('\r', '')
            else:
                idmlShortDescription = var_json['item']['product']['buyBox']['products'][0]['idmlSections'][
                    'idmlShortDescription']
                idmlLongDescription = var_json['item']['product']['buyBox']['products'][0]['idmlSections'][
                    'idmlLongDescription']

                description = str(idmlShortDescription) + str(idmlLongDescription)


            data['base']['productId'] = productId
            data['base']['title'] = title
            data['base']['currency'] = currency
            data['base']['stock'] = str(stock)
            data['base']['price'] = str(price)
            data['base']['priceRange'] = str(priceRange)
            data['base']['brand'] = brand
            data['base']['product_rating'] = product_rating
            data['base']['praise_rate'] = praise_rate
            data['base']['rating_number'] = rating_number
            data['images'] = index_img_list

            data['extension']['bulletPoint'] = bulletPoint
            data['extension']['description'] = description
            data['extension']['descriptionText'] = descriptionText



            # 多属性
            criteria = var_json['item']['product']['buyBox'].get('criteria')

            # 变体ID
            variable_Id = var_json['item']['product']['buyBox'].get('products')
            available_id_list = []
            for item_id in variable_Id:
                available_id_list.append(item_id['productId'])

            # 变体名的类型
            if criteria:
                name_type,color_name_list,size_name_list = self.variable_type(criteria)
            else:
                name_type = ''
                color_name_list = ''
                size_name_list = ''
            # print('name_type:', name_type)
            # print('color_name_list:', color_name_list)
            # print('size_name_list:', size_name_list)
            # print('\n')

            # 变体图
            images_list = var_json['item']['product']['buyBox'].get('images')
            images_list1 = var_json['item']['product']['buyBox']['products'][0].get('images')

            if images_list:
                img_dict = self.variable_img(images_list)

            elif images_list1:
                img_dict = {}
                img_i_list = []
                for i,img in enumerate(images_list):
                    print(img)
                    img_i_list.append(img['url'])
                    img_dict['img_{}'.format(i)] = img_i_list
            else:
                img_dict = '' # index_img_list



            # print('min_max_price:', min_max_price)
            # print('\n')

            # 变体组合
            try:
                states_list = var_json['item']['product']['buyBox'].get('states')
                color_fil = []
                color_img_dict = {}
                if states_list:
                    dict_result = self.variable_result(states_list,min_max_price,img_dict)

                    # 变体组装
                    variableList = []
                    count = 0
                    if color_name_list and size_name_list:
                        for i, color_name in enumerate(color_name_list):
                            for c, size_name in enumerate(size_name_list):
                                attributes_i = []
                                price_key = str(i) + ';' + str(c)
                                if count <= len(available_id_list):
                                    variable_productId = available_id_list[count]
                                    count += 1
                                else:
                                    variable_productId = ''
                                if price_key in dict_result:
                                    variab_price = dict_result[price_key]['price']
                                else:
                                    variab_price = ''
                                    stock = ''
                                color_name_pkey = name_type[color_name]['type']
                                name_type_pkey = name_type[size_name]['type']

                                base_i = {
                                    "productId": variable_productId,
                                    "title": str(title),
                                    "currency": str(currency),
                                    "price": variab_price,
                                    "stock": str(stock),
                                    "sales": ""
                                }
                                attri_i = {
                                    "pkey": color_name_pkey,
                                    "productId": variable_productId,
                                    "pval": color_name,
                                    "unit": ""
                                }
                                attri_ii = {
                                    "pkey": name_type_pkey,
                                    "productId": variable_productId,
                                    "pval": size_name,
                                    "unit": ""
                                }

                                attributes_i.append(attri_i)
                                attributes_i.append(attri_ii)
                                images_i = []
                                if price_key in dict_result and dict_result[price_key]['img']:
                                    print(33333333333,dict_result)
                                    for img in dict_result[price_key]['img']:
                                        img_i = {
                                            "type": 2,
                                            "imgUrl": img
                                        }
                                        images_i.append(img_i)
                                elif len(img_dict) == len(color_name_list):
                                        for img in img_dict['img_{}'.format(0)]:
                                            img_i = {
                                                "type": 2,
                                                "imgUrl": img
                                            }
                                            images_i.append(img_i)

                                else:
                                    # 通过color个数决定请求变体图片次数
                                    if 'Color' in str(color_name_pkey) and color_name not in color_fil:
                                        color_fil.append(color_name)
                                        detail_url = 'https://www.walmart.com/ip/' + str(variable_productId)
                                        images_i = self.get_detail_img(detail_url)
                                        color_img_dict[color_name] = images_i

                                    elif 'Color' in str(name_type_pkey) and size_name not in color_fil:
                                        color_fil.append(size_name)
                                        detail_url = 'https://www.walmart.com/ip/' + str(variable_productId)
                                        images_i = self.get_detail_img(detail_url)
                                        color_img_dict[size_name] = images_i

                                    print('2变体--橱窗图',color_name,size_name)
                                    if color_name in color_img_dict:
                                        images_i = color_img_dict[color_name]
                                    elif size_name in color_img_dict:
                                        images_i = color_img_dict[size_name]
                                    else:
                                        # for img in index_img_list:
                                        #     img_i = {
                                        #         "type": 2,
                                        #         "imgUrl": img['imgUrl']
                                        #     }
                                        #     images_i.append(img_i)
                                        print('img_dict为空', img_dict)# index_img_list

                                varia_i = {
                                    "base": base_i,
                                    "attributes": attributes_i,
                                    "images": images_i
                                }
                                variableList.append(varia_i)
                    elif color_name_list or size_name_list:
                        print(11111111111,img_dict)
                        if not size_name_list:
                            size_name_list = color_name_list
                        for c, size_name in enumerate(size_name_list):
                            attributes_i = []
                            price_key = str(c) + ';' + ''
                            if count <= len(available_id_list):
                                variable_productId = available_id_list[count]
                                count += 1
                            else:
                                variable_productId = ''
                            if price_key in dict_result:
                                variab_price = dict_result[price_key]['price']
                            else:
                                variab_price = ''
                                stock = ''
                            base_i = {
                                "productId": variable_productId,
                                "title": str(title),
                                "currency": str(currency),
                                "price": variab_price,
                                "stock": str(stock),
                                "sales": ""
                            }

                            attri_i = {
                                "pkey": name_type[size_name]['type'],
                                "productId": variable_productId,
                                "pval": size_name,
                                "unit": ""
                            }
                            attributes_i.append(attri_i)
                            detail_img = ''
                            images_i = []
                            if price_key in dict_result and dict_result[price_key]['img']:
                                for img in dict_result[price_key]['img']:
                                    img_i = {
                                        "type": 2,
                                        "imgUrl": img
                                    }
                                    images_i.append(img_i)
                            elif img_dict:

                                if len(img_dict) == len(size_name_list):
                                    for img in img_dict['img_{}'.format(c)]:
                                        img_i = {
                                            "type": 2,
                                            "imgUrl": img
                                        }
                                        images_i.append(img_i)
                                else:
                                    print(0000000000)
                            else:
                                print('1变体--橱窗图')
                                detail_url = 'https://www.walmart.com/ip/' + str(variable_productId)
                                detail_img = self.get_detail_img(detail_url)

                                if not detail_img:
                                    for img in index_img_list:
                                        img_i = {
                                            "type": 2,
                                            "imgUrl": img['imgUrl']
                                        }
                                        images_i.append(img_i)
                            print(444444444, size_name)
                            print(555555555, images_i)
                            print(666666666, detail_img)
                            varia_i = {
                                "base": base_i,
                                "attributes": attributes_i,
                                "images": detail_img if detail_img else images_i
                            }
                            variableList.append(varia_i)


                    data['variableList'] = variableList
            except Exception as e:
                print('变体Error:',e)
            print(json.dumps(data))
        else:
            print('获取不到详情json')
        return data
    def variable_img(self, images_list):
        img_dict = {}
        for i, imgs in enumerate(images_list):
            img_i_list = []
            for img in imgs:
                img_i_list.append(img['url'])
            img_dict['img_{}'.format(i)] = img_i_list
        return img_dict

    def variable_type(self, criteria):
        color_name_list = []
        size_name_list = []
        name_type = {}
        for i, items in enumerate(criteria):
            if 'values' in items:
                for att in items['values']:
                    item_dict = {
                        'swatch': '',
                        'images': ''
                    }
                    item_dict['type'] = items['name']
                    if i == 0:
                        color_name_list.append(att['title'])
                    elif i == 1:
                        size_name_list.append(att['title'])
                    if 'swatch' in att:
                        item_dict['swatch'] = att['swatch']
                    if 'images' in att:
                        item_dict['images'] = att['images']
                    name_type[att['title']] = item_dict
        return name_type,color_name_list,size_name_list

    def variable_result(self,states_list,min_max_price,img_dict):
        filter_jn = [] # 仅用于过滤重复
        price_product = {}
        li_list = []
        for i, k in enumerate(states_list):
            if k['action'] != 'NOT_AVAILABLE':
                pri = ''
                images_num = ''
                # if 'price' in k:
                #     pri = str(min_max_price['price_{}'.format(str(k['price']))])

                if 'images' in k and img_dict:
                    images_num = img_dict['img_{}'.format(str(k['images']))]

                if 'criteria' in k:
                    for j, s in enumerate(k['criteria'][0]['values']):

                        if 'product' in s and 'price' in s:
                            price_product[str(s['product'])] = s['price']
                        if 'product' in s and 'price' in k:
                            price_product[str(s['product'])] = k['price']

                        if s['availability'] == 'AVAILABLE' and s['next'] == i:
                            if 'price' in s:
                                pri = str(min_max_price['price_{}'.format(str(s['price']))])

                            if len(k['criteria'][0]['values']) == 2:
                                for n, m in enumerate(k['criteria'][-1]['values']):

                                    if m['availability'] == 'AVAILABLE':
                                        if str(m['product']) in price_product:
                                            m_id = 'price_{}'.format(str(m['product']))
                                            if not pri and m_id in min_max_price:
                                                pri = str(min_max_price[m_id])
                                            else:
                                                pri_price = price_product[str(m['product'])]
                                                pri = str(min_max_price['price_{}'.format(str(pri_price))])

                                        jn = str(j) + ';' + str(n)
                                        if jn not in filter_jn:
                                            data_list = (str(j), str(n), pri, images_num)
                                            li_list.append(data_list)
                                        filter_jn.append(jn)
                            else:
                                jn = str(j) + ';'
                                if jn not in filter_jn:
                                    data_list = (str(j), '', pri, images_num)
                                    li_list.append(data_list)
                                filter_jn.append(jn)
        dict_result = {}
        print('li_list:', li_list)
        for k in li_list:
            item_dict = {}
            key = k[0] + ';' + k[1]
            item_dict['price'] = k[2]
            item_dict['img'] = k[3]
            dict_result[key] = item_dict
        return dict_result

    def get_detail_img(self, url):
        header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?0',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
        }

        for useType in '012':
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            header['user-agent'] = userAgent().getPc()
            try:

                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                            timeout=5)
                html = result.text(self=WebRequest)
                print(len(html))
                var_obj_re = re.search(
                    re.compile('<script id="item" class="tb-optimized" type="application/json">(.*?)</script>',
                               re.DOTALL),
                    str(html))
                index_img_list = []
                if html:
                    if var_obj_re:

                        var_obj_re = str(var_obj_re.group()).replace(
                            '<script id="item" class="tb-optimized" type="application/json">', '').replace('</script>', '')
                        var_json = json.loads(var_obj_re)
                        print('111var_obj_re:', json.dumps(var_json))
                        images_i = var_json['item']['product']['buyBox']['products'][0]['images']

                        for img in images_i:
                            img_i_data = {
                                "type": 2,
                                "imgUrl": img['url']
                            }
                            index_img_list.append(img_i_data)
                        return index_img_list
                    elif 'Verify your identity' in str(html):
                        print('触发反爬')
                    elif 'Oops! This item is unavailable or on backorder' in str(html):
                        print('url Error')
                else:
                    continue
            except Exception as e:
                print('detail_Error:',e)

    def resetClassVar(self):
        self.proxyIpPortList = []