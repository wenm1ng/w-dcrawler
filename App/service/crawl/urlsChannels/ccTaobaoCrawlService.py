# -*- coding: utf-8 -*-
import itertools
from functools import reduce

import random
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

import demjson
import requests
import hashlib
import datetime

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


def get_discount_price(itemid, sellerid):
    url = 'https://detailskip.taobao.com/service/getData/1/p2/item/detail/sib.htm?itemId={}&sellerId={}&modules=dynStock,qrcode,viewer,price,duty,xmpPromotion,delivery,activity,fqg,zjys,amountRestriction,couponActivity,soldQuantity,page,originalPrice,tradeContract&callback=onSibRequestSuccess'.format(
        itemid, sellerid)
    headers = {
        "referer": "https://item.taobao.com/item.htm?ft=t&id={}".format(itemid)}
    resp = requests.get(url, headers=headers)
    discount_price_data = re.search('onSibRequestSuccess\(({[\s\S]*?})\)', resp.text).group(1)
    return discount_price_data


def get_taobao_prop_data(emt):
    data = {
        "pid": "",
        "name": "",
        "values": []
    }
    name = emt.xpath('./@data-property')[0]
    data['name'] = name

    pid = emt.xpath('./li[1]/@data-value')[0]
    data['pid'] = pid[:pid.index(':')]

    li_list = emt.xpath('.//li')
    for i in li_list:
        vid_xpath = i.xpath('./@data-value')[0]
        propid = vid_xpath[:vid_xpath.index(':')]
        vid = vid_xpath[vid_xpath.index(':') + 1:]
        skuname = i.xpath('./a/span/text()')[0]

        if propid == '1627207':
            vid_xpath = i.xpath('./a/@style')
            if vid_xpath == []:
                vid_xpath = ''
            else:
                vid_xpath = vid_xpath[0].replace("background:url(", "http:").replace(") center no-repeat;", '')
                vid_xpath = re.sub('\.jpg[\s\S]*', '.jpg', vid_xpath)
            value_i = {
                "vid": vid,
                "name": skuname,
                "image": vid_xpath
            }
        else:
            value_i = {
                "vid": vid,
                "name": skuname
            }
        data['values'].append(value_i)

    return data


def get_sku_mapping(HTML):
    sku_mapping = {}
    sku_xpath = HTML.xpath("//div[@id='J_isku']/div[@class='tb-skin']")[0]
    ns = {"re": "http://exslt.org/regular-expressions"}
    qqq = sku_xpath.xpath("//dl[re:match(@class,'J_Prop.*?tb-prop tb-clear.*?')]", namespaces=ns)
    propid = []
    propval = []
    for qqq_i in qqq:
        prop_a_id = qqq_i.xpath('./dd//li/@data-value')
        prop_a_k = qqq_i.xpath('./dt/text()')
        prop_a_v = qqq_i.xpath('./dd//li/a/span/text()')
        propid.append(prop_a_id)
        propval.append(list(itertools.product(prop_a_k, prop_a_v)))
    #
    # print(list(itertools.product(tuple(propid))))
    fn = lambda x, code=';': reduce(lambda x, y: [str(i) + code + str(j) for i in x for j in y], x)  # 多列表组合
    tt = fn(propid)
    tt1 = fn(propval)
    mapping_data = tuple(zip(tt, tt1))
    for i in mapping_data:
        sku_mapping.update({i[0]: i[1]})
    return sku_mapping


def get_sku_img_mapping(Html):
    sku_img_mapping = {}
    img_a_k = Html.xpath('//ul[@class="J_TSaleProp tb-img tb-clearfix"]/li/@data-value')
    if not img_a_k:
        img_a_k = Html.xpath('////ul[@class="J_TSaleProp tb-clearfix"]/li/@data-value')
    img_a_v = Html.xpath('//ul[@class="J_TSaleProp tb-img tb-clearfix"]/li/a')
    # img_a_v没有style时两者长度不同，样式会乱
    img_a_v_list = []
    for i in img_a_v:
        img_a_v_i = i.xpath('./@style')
        if img_a_v_i:
            img_a_v_i = img_a_v_i[0]
        else:
            img_a_v_i = ''
        img_a_v_list.append(img_a_v_i)
    img = tuple(zip(img_a_k, img_a_v_list))
    for i in img:
        k = str(i[0])
        v = i[1].replace('background:url(', '').replace(')', '').replace(' center no-repeat;', '')
        if v:
            v = 'https:' + v
        if k and v:
            sku_img_mapping.update({k: v})
    if not sku_img_mapping and img_a_k:
        for i in img_a_k:
            sku_img_mapping[i] = ''
    return sku_img_mapping


def get_desc(itemid):
    url = 'https://mdetail.tmall.com/templates/pages/desc?id={}'.format(itemid)
    resp = requests.get(url, timeout=5)
    descUrldata = re.search('Desc.init\((.*?)\);', resp.text).group(1)
    try:
        descUrl = json.loads(descUrldata)['TDetail']['product_tasks']['descUrl']
    except KeyError:
        descUrl = json.loads(descUrldata)['TDetail']['api']['descUrl']
    desc = requests.get("https:" + descUrl, timeout=5)
    return desc


class ccTaobaoCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Taobao'

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

        itemid = re.search("http.*?id=(\d+).*?", url).group(1)  # 淘宝的id
        md5str = hashlib.md5('{}'.format(itemid).encode(encoding='UTF-8')).hexdigest()
        itemid_validity = commonRedisClass.zscoreValByKey('taobao_info', '{}'.format(md5str))
        now_time = time.time()
        if itemid_validity != None:
            print('有缓存')
            shijiancha = int(now_time - itemid_validity)
            if shijiancha >= defaultApp.taobao_life_time['info']:
                print('已过期')
            else:
                print('没过期')
                print('http://47.107.142.65:9200/taobao_info/_doc/{itemid}'.format(itemid=md5str))
                data = commonElasticSearchClass.getSourceByIndexKey(index='taobao_info', doc_type="_doc", id=md5str)
                self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                return

        header = {
            'Cache-Control': 'no-cache',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': 'cna=3PuUGdKY8BoCAQ4Su3ut40eh; t=8f6dc9057ef4711c9e57d7b06e54aa23; sgcookie=E100g%2BCMfG6%2Bz8vBnS8CxtlPJYz8UwLuFDLs2DAgQBQvN5CcErQmK0aZHByUhUJFge8wO%2BAWsfUUpWzU53a96SuWQ5dasTcCSer2L66RTZV36gc%3D; uc3=nk2=F5RFh6jNB14tcWw%3D&vt3=F8dCujaOWgLG7AmNuJI%3D&id2=UNk1%2Br2BfHAWow%3D%3D&lg2=W5iHLLyFOGW7aA%3D%3D; lgc=tb076241109; uc4=id4=0%40Ug4%2FEBPRLzVMHptqkHXrMTyfHkXT&nk4=0%40FY4O7oHcpA52ZeBDzVoDiyLpBf1oAg%3D%3D; tracknick=tb076241109; _cc_=WqG3DMC9EA%3D%3D; enc=ZNFbsA91tUYmFq7a5Pghd4YcxEDSHOf4hnJYPjPBV6fiqt3KGYEoY9sKY0cOKpEFN5NCdvBh1tG19xG4kNCjbQ%3D%3D; cookie2=18547b21a72b5dfd84a1c1fb821cf529; _tb_token_=75d138aed1833; mt=ci=-1_0; thw=cn; xlly_s=1; hng=CN%7Czh-CN%7CCNY%7C156; _samesite_flag_=true; uc1=cookie14=Uoe3c9ovSJxuoA%3D%3D; l=eB_jcaqIgibDxiCoKOfwourza77OSIRAguPzaNbMiOCP9tfe5YuAW6EUHiLwC3GVhs_HR37c4VqbBeYBqS0H3CPie5DDwQHmn; isg=BJqaNe68r_v-kiNsVyBSMwEo60C8yx6lXlqKB6QTRi34FzpRjFtutWDl5-OLx5Y9; tfstk=cqOOBQxqeDmize_pzdHnl-mYcLdAZ2oAAPs0M2eZQPn0NGNAi7RkwuLmCZsPX2C..',
            'Content-Type': 'Content-type:text/html;charset=gbk'
        }
        for useType in '0121212':
            header['USETYPE'] = useType
            header['TARGETURL'] = url
            header['user-agent'] = userAgent().getPc()

            try:
                proxies = {
                    'http': 'http://120.77.46.4:6666',
                    'https': 'http://120.77.46.4:6666'
                }
                result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,proxies=proxies,
                                            timeout=5)
                if len(result.text(self=WebRequest)) < 10000:
                    continue
                result_data = result.text(self=WebRequest)

                print(len(result_data))
                data = self.setResult(result_data, url)  # 洗完的结构
                print(666, data)
                if data:
                    self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                    commonElasticSearchClass.insertDataByIndexKey(index='taobao_info', id=md5str, data=data)
                    commonRedisClass.insertDataByIndexKey(redisKeyName='taobao_info', redisStr=md5str)
                    self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                else:
                    continue
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
                "quantity": "",
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
        var_g_config_re = re.search("var g_config = ({[\s\S]*?});", sourceHtml)
        if var_g_config_re == None:
            print('获取数据1失败')
            return
        var_g_config = var_g_config_re.group(1)
        var_g_config = var_g_config.replace('!true', 'true').replace('ifalse', '').replace('-', '').replace(' ',
                                                                                                            '').replace(
            '\n', '')
        var_g_config = re.sub("descUrl.*?:'.*?,", '', var_g_config).replace("+newDate,", "'',")
        var_g_config = demjson.decode(var_g_config)  # 淘宝页面   上的json.data 转回python的json对象

        itemid = var_g_config['idata']['item']['id']
        data['base']['productId'] = itemid

        title = var_g_config['idata']['item']['title']
        data['base']['title'] = title

        sellerid = var_g_config['sellerId']

        HTML = etree.HTML(sourceHtml)
        # 掌柜:contact_seller
        contact_seller_re = re.findall("sellerNick       : '(.*?)',", sourceHtml)
        if contact_seller_re:
            data['base']['contact_seller'] = contact_seller_re[0]
        # 商家名称
        mall_name_xpath = HTML.xpath('//div[@class="tb-shop-name"]/dl/dd/strong/a/@title')
        if mall_name_xpath:
            data['base']['mall_name'] = mall_name_xpath[0]
        else:
            mall_name_re = re.findall("请进入.*?的(.*?)实力旺铺", sourceHtml)
            if mall_name_re:
                data['base']['mall_name'] = mall_name_re[0]

        # 尺寸
        size_unit = ['m', 'dm', 'cm', 'mm', 'M', 'DM', 'CM', 'MM', '米', '分米', '厘米', '毫米', 'X', '*']
        info2 = []
        descriptionText = ""
        propsCut_data_name_xpath = HTML.xpath('//*[@class="attributes-list"]/li/text()')
        if propsCut_data_name_xpath:
            info = [i.replace('\xa0', '') for i in propsCut_data_name_xpath]
            for attr_data in info:
                attr_data_i = attr_data.split(':')
                data_i = {
                    "productId": str(itemid),
                    "pkey": attr_data_i[0],
                    "pval": attr_data_i[1],
                    "unit": ""
                }
                info2.append(data_i)
                # 新增品牌
                if '品牌' in attr_data_i[0]:
                    data['base']['brand'] = attr_data_i[1]
                # 新增尺寸
                if '尺寸' in attr_data_i[0] or '规格' in attr_data_i[0]:
                    for item in size_unit:
                        if item in attr_data_i[1] and '*' in attr_data_i[1] or 'x' in attr_data_i[1] and 'L' not in \
                                attr_data_i[1]:
                            if len(attr_data_i[1]) < 20:
                                data['base']['size'] = attr_data_i[1]
                            else:
                                pass
                                # print('尺寸过长',attr_data_i[1])
                # 新增毛重
                if '毛重' in attr_data_i[0] or '重量' in attr_data_i[0] or '净含量' in attr_data_i[0]:

                    data['base']['weight_value'] = str(attr_data_i[1]).replace('kg', '').replace('g', '')
                    if 'kg' in attr_data_i[1]:
                        data['base']['weight_unit'] = 'kg'
                    elif 'g' in attr_data_i[1]:
                        data['base']['weight_unit'] = 'g'
                    elif 'kg' in attr_data_i[0]:
                        data['base']['weight_unit'] = 'kg'
                    elif 'g' in attr_data_i[0]:
                        data['base']['weight_unit'] = 'g'
            data['attributes'] = info2

            descriptionTextlist = []
            for i in info:
                attr_data_i = i.split(':')
                infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=attr_data_i[0],
                                                                                value=attr_data_i[1])
                descriptionTextlist.append(infostr)
            descriptionText = ''.join(descriptionTextlist)
            data['extension']['descriptionText'] = descriptionText

        imglist2 = []
        images_xpath = HTML.xpath('//*[@id="J_UlThumb"]/li/div/a/img/@data-src')
        if images_xpath:
            for i in images_xpath:
                imgUrl = i.replace('//gd', 'https://gd')
                imgUrl = re.sub('_\d+x\d+.*?.jpg', '', imgUrl)
                img_i = {
                    "type": "0",
                    "imgUrl": imgUrl
                }
                imglist2.append(img_i)

        desc = get_desc(itemid)  # 描述图
        if desc:
            data['extension']['description'] = descriptionText + str(desc.text).replace("var desc='",'')
            desc_HTML = etree.HTML(desc.text)
            detillimg_xpath = desc_HTML.xpath('/html/body//img/@src')
            if detillimg_xpath:
                for i in detillimg_xpath:
                    img_i = {
                        "type": "1",
                        "imgUrl": i,
                    }
                    imglist2.append(img_i)

        data['images'] = imglist2

        discount_price_data = get_discount_price(itemid, sellerid)  # 获取打折价

        if discount_price_data:
            discount_price_data_dict = json.loads(discount_price_data)
        else:
            print('获取sku价格失败')
            return
        print(json.dumps(discount_price_data_dict))
        total_stock = discount_price_data_dict['data']['dynStock']['stock']
        data['base']['quantity'] = str(int(total_stock))
        try:
            yuanjia = discount_price_data_dict['data']['promotion']['promoData']['def'][0]['price'].split("-")[0]
            discount_price_data_dict_sku_price = discount_price_data_dict['data']['promotion']['promoData']
        except KeyError:
            yuanjia = discount_price_data_dict['data']['price'].split("-")[0]
            discount_price_data_dict_sku_price = discount_price_data_dict['data']['originalPrice']
            if '-' in discount_price_data_dict['data']['price']:
                data['base']['priceRange'] = str(discount_price_data_dict['data']['price']).replace('-','~')
        data['base']['price'] = str(float(yuanjia))
        discount_price_data_dict_sku_stock = discount_price_data_dict['data']['dynStock'].get('sku')

        Hub_config = re.search("Hub.config.set\('sku', ({[\s\S]*?})\);", sourceHtml).group(1)
        skuMap = demjson.decode(Hub_config)['valItemInfo'].get('skuMap')

        variableList2 = []
        sku_img_mapping = get_sku_img_mapping(HTML)
        try:
            sku_mapping = get_sku_mapping(HTML)
        except:
            sku_mapping = ''
        print('sku_img_mapping:',sku_img_mapping)
        if sku_img_mapping:
            for i, j in sku_mapping.items():
                str_k = ';' + i + ';'
                try:
                    price_data = discount_price_data_dict_sku_price[str_k]
                    if type(price_data) == list:
                        price = price_data[0]['price']
                    elif type(price_data) == dict:
                        price = price_data['price']
                    else:
                        price = "0"
                except KeyError:
                    price = "0"

                try:
                    pstock_data = discount_price_data_dict_sku_stock[str_k]
                    if type(pstock_data) == list:
                        pstock = pstock_data[0]['stock']
                    elif type(pstock_data) == dict:
                        pstock = pstock_data['stock']
                    else:
                        pstock = "0"
                except KeyError:
                    pstock = "0"

                skuid = str(skuMap[str_k]['skuId'])
                base_i = {
                    "productId": skuid,
                    "title": str(title),
                    "currency": "CNY",
                    "price": float(price),
                    "priceRange": '',
                    "stock": pstock,
                    "sales": 0
                }
                attributes_i = []
                if type(j) == tuple:
                    attr_i = {
                        "pkey": j[0],
                        "productId": str(itemid),
                        "pval": j[1],
                        "unit": ""
                    }
                    attributes_i.append(attr_i)
                else:
                    for k in j.split(';'):
                        k = k.replace('(', '').replace(')', '').replace("'", '').split(',')
                        attr_i = {
                            "pkey": k[0],
                            "productId": str(itemid),
                            "pval": k[1],
                            "unit": ""
                        }
                        attributes_i.append(attr_i)
                sku_imglist = []
                if str(i) in sku_img_mapping:
                    imgUrl = re.sub('_\d+x\d+.*?.jpg', '', sku_img_mapping[str(i)])
                    img_data = {
                        "type": "3",
                        "imgUrl": imgUrl
                    }
                    sku_imglist.append(img_data)
                else:
                    if ';' in i:
                        img_list = i.split(';')
                    elif ':' in i:
                        img_list = i.split(':')
                    else:
                        img_list = i

                    for uu in img_list:
                        try:
                            imgUrl = re.sub('_\d+x\d+.*?.jpg', '', sku_img_mapping[str(uu)])
                            img_data = {
                                "type": "3",
                                "imgUrl": imgUrl
                            }
                            sku_imglist.append(img_data)
                        except Exception as e:
                            print('img_error::::::',e)
                            continue
                skudata = {
                    "base": base_i,
                    "attributes": attributes_i,
                    "images": sku_imglist
                }
                variableList2.append(skudata)

        data['variableList'] = variableList2

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
