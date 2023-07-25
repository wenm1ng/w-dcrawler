# coding: utf-8
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
import hashlib
import datetime

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class ccMobileyangkeduoCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Mobileyangkeduo'

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

    def saveHtmlResult(self, url):
        commonRedisClass = commonRedis()
        commonElasticSearchClass = commonElasticSearch()
        itemid = ''
        cook = ''
        urlsInfo = urlparse(url)

        if urlsInfo:
            if urlsInfo.netloc == 'pifa.pinduoduo.com':
                itemid = re.search('gid=(\d+)?', urlsInfo.query)
                if itemid:
                    itemid = itemid.group(1)
                    url = 'https://mobile.yangkeduo.com/goods.html?goods_id={}'.format(itemid)
                else:
                    itemid = ''
            else:
                queryParam = parse_qs(urlsInfo.query)
                if queryParam:
                    if 'goods_id' in queryParam:
                        itemid = queryParam['goods_id'][0]
        md5str = itemid
        itemid_validity = commonRedisClass.zscoreValByKey(redisKeyName='pdd_info', value='{}'.format(md5str))
        now_time = time.time()

        # if itemid_validity != None:
        #     print('有缓存')
        #     shijiancha = int(now_time - itemid_validity)
        #     if shijiancha >= defaultApp.pdd_life_time['info']:
        #         print('已过期')
        #     else:
        #         print('没过期')
        #         print('http://47.107.142.65:9200/pdd_info/_doc/{itemid}'.format(itemid=md5str))
        #         data = commonElasticSearchClass.getSourceByIndexKey(index='pdd_info', doc_type="_doc", id=md5str)
        #         self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
        #         self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
        #         return
        header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'max-age=0',
            "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'sec-ch-ua-mobile': '?1',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'referer': url + "&refer_page_name=login&refer_page_id=&refer_page_sn=" if 'refer_page_id' not in url  else url,
            }
        pddHtmlResult = False
        pdd_token_pool_length = commonRedisClass.zcardByKey('pdd_client_mobile_token')  # 获取cook池长度
        if pdd_token_pool_length:
            print('====================redis=====================')
            for i in range(5):
                cookList = commonRedisClass.zrevrangeByKey('pdd_client_mobile_token')  # 获取cook池长度
                print('剩余cook:', len(cookList))
                if cookList:
                    cook = random.choices(cookList)[0].replace('\r', '').replace('\n', '').replace(' ', '')
                header['cookie'] = 'PDDAccessToken=' + cook
                header['user-agent'] = userAgent().getAndroid()
                try:
                    result = WebRequest.easyGet(self=WebRequest, url=url, header=header, timeout=5)
                    window_rawData = re.search(r'window.rawData=(.*}});', result.text(self=WebRequest),
                                               re.M | re.I).group(
                        1)
                    if self.isTrueHtml(window_rawData, url):
                        data = self.setResult(window_rawData, url)  # 洗完的结构

                        self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                        commonElasticSearchClass.insertDataByIndexKey(index='pdd_info', id=md5str, data=data)
                        commonRedisClass.insertDataByIndexKey(redisKeyName='pdd_info', redisStr=md5str)
                        self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                        commonRedisClass.zincrbyValByKey(redisKeyName='pdd_client_mobile_token',
                                                         value=cook)  # 此cook 加一分

                        pddHtmlResult = True
                        return
                except Exception as e:
                    commonRedisClass.zremValByKey(redisKeyName='pdd_client_mobile_token', value=cook)  # 移除
                    print(e)
                    continue

        if pddHtmlResult == False:
            print('===================proxy=====================')
            for useType in '0112233':
                print(111, useType)
                header['USETYPE'] = useType
                header['TARGETURL'] = url
                header['user-agent'] = userAgent().getAndroid()
                try:
                    result = WebRequest.easyGet(self=WebRequest, url=defaultApp.szListingDynamicProxyUrl, header=header,
                                                timeout=5)
                    window_rawData = re.search(r'window.rawData=(.*}});', result.text(self=WebRequest),
                                               re.M | re.I).group(1)

                    if self.isTrueHtml(window_rawData, url):

                        data = self.setResult(window_rawData, url)  # 洗完的结构
                        print(6666,json.dumps(data))
                        if data:
                            self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                            commonElasticSearchClass.insertDataByIndexKey(index='pdd_info', id=md5str, data=data)
                            commonRedisClass.insertDataByIndexKey(redisKeyName='pdd_info', redisStr=md5str)
                            self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                            return
                        else:
                            continue
                    else:
                        continue
                except Exception as e:
                    print(e)
        else:
            for i in range(3):
                cookList = commonRedisClass.zrevrangeByKey('pdd_client_mobile_token')  # 获取cook池长度
                print('剩余cook:', len(cookList))
                if cookList:
                    cook = random.choices(cookList)[0].replace('\r', '').replace('\n', '').replace(' ', '')
                header['cookie'] = 'PDDAccessToken=' + cook
                header['user-agent'] = userAgent().getAndroid()
                try:
                    result = WebRequest.easyGet(self=WebRequest, url=url, header=header, timeout=5)
                    window_rawData = re.search(r'window.rawData=(.*}});', result.text(self=WebRequest),
                                               re.M | re.I).group(
                        1)
                    if self.isTrueHtml(window_rawData, url):
                        data = self.setResult(window_rawData, url)  # 洗完的结构

                        self.relayServiceClass.postProductCenterLinkJsonResult(data=data)
                        commonElasticSearchClass.insertDataByIndexKey(index='pdd_info', id=md5str, data=data)
                        commonRedisClass.insertDataByIndexKey(redisKeyName='pdd_info', redisStr=md5str)
                        self.relayServiceClass.delUrlsCrawlerSuccessByUrl(url=url)
                        commonRedisClass.zincrbyValByKey(redisKeyName='pdd_client_mobile_token',
                                                         value=cook)  # 此cook 加一分
                        return
                except Exception as e:
                    commonRedisClass.zremValByKey(redisKeyName='pdd_client_mobile_token', value=cook)  # 移除
                    print(e)
                    continue

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
        if len(htmlText) > 5000:
            flag = True
        return flag

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
                "mall_name": ""
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
        dataList = json.loads(sourceHtml)
        itemid = dataList['store']['initDataObj']['goods']['goodsID']
        data['base']['productId'] = itemid

        title = dataList['store']['initDataObj']['goods']['goodsName']
        data['base']['title'] = title

        min_price = dataList['store']['initDataObj']['goods']['minGroupPrice']
        data['base']['price'] = min_price

        max_price = dataList['store']['initDataObj']['goods']['maxGroupPrice']
        data['base']['priceRange'] = str(min_price) + '~' + str(max_price)

        sales = dataList['store']['initDataObj']['goods']['sideSalesTip']  # 数字提取
        sales_num = re.search('.*?(\d+\.\d+|\d+)', sales).group(1)
        if sales_num:
            if '万' in sales:
                sales = float(sales_num) * 10000
            else:
                sales = float(sales_num)
            data['base']['sales'] = sales

        quantity = dataList['store']['initDataObj']['goods']['quantity']
        data['base']['quantity'] = quantity

        comments_number = dataList['store']['initDataObj']['oakData']['review']['reviewNum']
        data['base']['comments_number'] = comments_number

        mall_id = dataList['store']['initDataObj']['mall']['mallId']
        data['base']['mall_id'] = mall_id

        mall_link = 'https://mobile.yangkeduo.com/mall_page.html?mall_id={}'.format(mall_id)
        data['base']['mall_link'] = mall_link

        mall_name = dataList['store']['initDataObj']['mall']['mallName']
        data['base']['mall_name'] = mall_name

        # 综合评分
        mallStar = dataList['store']['initDataObj']['mall']['dsr'].get('mallStar')
        data['base']['product_rating'] = mallStar

        imglist2 = []
        topGallery = dataList['store']['initDataObj']['goods']['topGallery']
        for i in topGallery:
            img_data_i = {
                "type": "0",
                "imgUrl": i['url']
            }
            imglist2.append(img_data_i)

        try:
            detailGallery = dataList['store']['initDataObj']['oakData']['goods']['decoration']
        except:
            detailGallery = ''
        if not detailGallery:
            detailGallery = dataList['store']['initDataObj']['goods']['detailGallery']

        detail_img = []
        for i in detailGallery:
            img_data_i = {
                "type": "1",
                "imgUrl": [i['url'] if 'url' in i else i['contents'][0]['imgUrl']][0],
            }

            detail_img.append(img_data_i)
        data['images'] = imglist2

        info2 = []
        for n,i in enumerate(dataList['store']['initDataObj']['goods']['goodsProperty']):
            productId = int(str(itemid) + '{}'.format(n))
            pdata = {
                "pkey": i['key'],
                "productId": productId,
                "pval": i['values'][0],
                "unit": ""
            }
            info2.append(pdata)
        data['attributes'] = info2

        variableList2 = []
        for i,sku_i in enumerate(dataList['store']['initDataObj']['goods']['skus']):

            base_data = {
                "productId": sku_i['skuId'],
                "title": title,
                "currency": "CNY",
                "price": sku_i['groupPrice'],
                "priceRange": "",
                "stock": sku_i['quantity'],
                "sales": 0,
            }
            attributes_data = []
            for c,j in enumerate(sku_i['specs']):
                productId = int(str(sku_i['skuId']) + '{}'.format(i))
                attributes_i = {
                    "pkey": j['spec_key'],
                    "productId": str(productId) + '{}'.format(c),
                    "pval": j['spec_value'],
                    "unit": ""
                }
                attributes_data.append(attributes_i)
            images_data = [
                {
                    "type": 3,
                    "imgUrl": sku_i['thumbUrl']
                }
            ]
            vdata = {
                "base": base_data,
                "attributes": attributes_data,
                "images": images_data,
            }
            variableList2.append(vdata)
        data['variableList'] = variableList2
        descriptionTextlist = []
        for i in dataList['store']['initDataObj']['goods']['goodsProperty']:
            infostr = '<div title="{value}">{key}:&nbsp;{value}</div>'.format(key=i['key'], value=i['values'][0])
            descriptionTextlist.append(infostr)
        descriptionText = ''.join(descriptionTextlist)
        data['extension']['descriptionText'] = descriptionText

        descriptionlist = []
        for i in detail_img:
            imgstr = '<img src="{}">'.format(i['imgUrl']) + '<br/>'
            descriptionlist.append(imgstr)
        description = '<div>' + ''.join(descriptionlist) + '</div>'
        data['extension']['description'] = descriptionText + description
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
