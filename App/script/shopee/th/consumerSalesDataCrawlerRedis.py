#!/usr/bin/python
# -*- coding:utf-8 -*-
import datetime
import hashlib
import json
import sys,os
import time

import requests

o_path = os.getcwd()
sys.path.append(o_path)

from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.userAgent import userAgent
from App.common.funs import getFirstRightValueByMark


def get_sales(sale31_list):
    data = {
        "three_day_sold": -1,
        "seven_day_sold": -1,
        "fifteen_day_sold": -1,
        "thirty_day_sold": -1
    }
    if sale31_list == []:
        return data
    else:
        if len(sale31_list) >= 31:
            sales3 = sale31_list[-1] - sale31_list[-4]
            sales7 = sale31_list[-1] - sale31_list[-8]
            sales15 = sale31_list[-1] - sale31_list[-16]
            sales30 = sale31_list[-1] - sale31_list[-30]
            data.update({
                "three_day_sold": sales3,
                "seven_day_sold": sales7,
                "fifteen_day_sold": sales15,
                "thirty_day_sold": sales30
            })

        elif len(sale31_list) >= 16:
            sales3 = sale31_list[-1] - sale31_list[-4]
            sales7 = sale31_list[-1] - sale31_list[-8]
            sales15 = sale31_list[-1] - sale31_list[-16]
            data.update({
                "three_day_sold": sales3,
                "seven_day_sold": sales7,
                "fifteen_day_sold": sales15
            })

        elif len(sale31_list) >= 8:
            sales3 = sale31_list[-1] - sale31_list[-4]
            sales7 = sale31_list[-1] - sale31_list[-8]
            data.update({
                "three_day_sold": sales3,
                "seven_day_sold": sales7
            })

        elif len(sale31_list) >= 4:
            sales3 = sale31_list[-1] - sale31_list[-4]
            data.update({"three_day_sold": sales3})

        return data


def get_md5(str):
    strmd5 = hashlib.md5(str.encode(encoding='UTF-8')).hexdigest()
    return strmd5


def getcreg(categories):
    dataee = {}
    for i, j in enumerate(categories):
        dataee.update({i: j})
    return dataee


def setResult(sourceHtml, url, Shopee_country):
    print(url)
    data = {
        'extra_data': [],
        'base': {
            "productId": "",
            "title": "",
            "title_en": "",
            "brand": '',
            "sourceUrl": "",
            "site": "",
            "currency": "",
            "price": "",
            "priceRange": "",
            "siteLanguage": "en",
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
            "monthly_sales": "",  # 平台自有月销量
            "categories_bag": {},
            "sales_bag": {

            },
            "delivery_bag": {
                "Free_shipping": -1,
                "Shipping": -1
            },
            "estimated_days": -1,  # 发货天数
            "product_rating": -1,  # 商品评分
            "comments_number": -1,  # 评论数量
            "collection_volume": "",  # 收藏量
            "praise_rate": "",  # 好评率
            "quantity": "",
            "mall_id": "",
            "mall_link": "",
            "mall_name": ""
        },
        "image": '',
        'images': [],
        'attributes': [],
        'variableList': [],
        'is_valid': '',
        'extra': '',
        'extension': {
            'descriptionText': "",
            'description': ""
        },
        'sales31': [],
        "update_timestamp": int(time.time()),
        "update_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    }

    data['base']['sourceUrl'] = url

    sourceHtml_dict = json.loads(sourceHtml)

    itemid = sourceHtml_dict['item']['itemid']
    data['base']['productId'] = itemid

    shopid = sourceHtml_dict['item']['shopid']
    data['base']['mall_id'] = shopid

    title = sourceHtml_dict['item']['name']
    data['base']['title_en'] = title

    price = sourceHtml_dict['item']['price'] / 100000

    data['base']['price'] = price

    location = sourceHtml_dict['item']['shop_location']
    data['base']['location'] = location

    sales = sourceHtml_dict['item']['historical_sold']
    data['base']['sales'] = sales

    monthly_sales = sourceHtml_dict['item']['sold']
    data['base']['monthly_sales'] = monthly_sales

    categories = sourceHtml_dict['item']['categories']
    catidlist = [-1 if i['catid'] == None else i['catid'] for i in categories]
    categories_bag = getcreg(catidlist)
    data['base']['categories_bag'] = categories_bag

    product_rating = sourceHtml_dict['item']['item_rating']['rating_star']
    data['base']['product_rating'] = product_rating

    quantity = sourceHtml_dict['item']['stock']
    data['base']['quantity'] = quantity

    estimated_days = sourceHtml_dict['item']['estimated_days']
    data['base']['quantity'] = estimated_days

    comments_number = sourceHtml_dict['item']['item_rating']['rating_count'][0]
    data['base']['comments_number'] = comments_number

    site = Shopee_country.upper()
    data['base']['site'] = site

    currency = sourceHtml_dict['item']['currency']
    data['base']['currency'] = currency

    mall_id = sourceHtml_dict['item']['shopid']
    data['base']['mall_id'] = mall_id

    mall_link = 'https://{}/shop/{}/search'.format(domain_list[Shopee_country], mall_id)
    data['base']['mall_link'] = mall_link

    image = sourceHtml_dict['item']['image']
    data['image'] = image

    imglist2 = []
    for img_i in sourceHtml_dict['item']['images']:
        img_i_data = {
                         "type": 0,
                         "imgUrl": 'https://cf.shopee.co.th/file/' + str(img_i)
                     },
        imglist2.append(img_i_data[0])
    data['images'] = imglist2

    data['base']['currency'] = currency

    info2 = []
    attributes = sourceHtml_dict['item']['attributes']
    for attr_i in attributes:
        data_i = {
            "productId": itemid,
            "pkey": attr_i['name'],
            "pval": attr_i['value'],
            "unit": ""
        }
        info2.append(data_i)
    data['attributes'] = info2

    variableList2 = []

    sku_img_mapping2 = {}
    tier_var_name = sourceHtml_dict['item']['tier_variations']
    if tier_var_name == []:
        pass
    else:
        tier_var_name = sourceHtml_dict['item']['tier_variations'][0]['name']
        sku_img_name = sourceHtml_dict['item']['tier_variations'][0]['options']
        sku_img = sourceHtml_dict['item']['tier_variations'][0]['images']
        sku_img_mapping = tuple(zip(sku_img_name, sku_img))
        for i in sku_img_mapping:
            sku_img_mapping2.update({i[0]: i[1]})

    models = sourceHtml_dict['item']['models']
    for models_i in models:
        base_i = {
            "productId": models_i['modelid'],
            "title": models_i['name'],
            "currency": currency,
            "price": float(int(models_i['price']) / 100000),
            "priceRange": "",
            "stock": models_i['stock'],
            "sales": models_i['sold']
        }

        attributes_i = []
        attr_i = {
            "pkey": tier_var_name,
            "productId": str(itemid),
            "pval": models_i['name'],
            "unit": ""
        }
        attributes_i.append(attr_i)

        sku_imglist = []
        try:
            img = 'https://cf.shopee.co.th/file/' + sku_img_mapping2[models_i['name']]
            img_data = {
                "type": "3",
                "imgUrl": img
            }
            sku_imglist.append(img_data)
        except:
            pass

        varia_i = {
            "base": base_i,
            "attributes": attributes_i,
            "images": sku_imglist
        }
        variableList2.append(varia_i)
    data['variableList'] = variableList2

    descriptionTextlist = []
    for attr_i in attributes:
        infostr = '<li title="{value}">{key}:&nbsp;{value}</li>'.format(key=attr_i['name'], value=attr_i['value'])
        descriptionTextlist.append(infostr)
    descriptionText = '<ul>' + ''.join(descriptionTextlist) + '</ul>'
    data['extension']['descriptionText'] = descriptionText

    description = sourceHtml_dict['item']['description']
    data['extension']['description'] = descriptionText + description

    data['sales31'] = [sales]
    # print(json.dumps(data))
    return data
    # desc_req = self.session.get(desc_url, headers=self.desc_headers, timeout=10)
    # result = self.parse_description(desc_req, product_data)
    # result_json = json.dumps(result)
    # sentinelServMaster.lpush(self.item_key, result_json)

domain_list = {
    'th': 'shopee.co.th',
    'sg': 'shopee.sg',
    'id': 'shopee.co.id',
    'my': 'shopee.com.my',
    'vn': 'shopee.vn',
    'ph': 'shopee.ph',
    'tw': 'xiapi.xiapibuy.com',
    'br': 'shopee.com.br'
}


def execMain():
    commonRedisClass = commonRedis()
    commonElasticSearchClass = commonElasticSearch()

    Shopee_country = getFirstRightValueByMark(matchString=os.path.dirname(__file__), mark=os.sep)

    redis_indexname = "shopee_url_{}".format(Shopee_country)
    redis_indexname_del = "shopee_url_{}_del".format(Shopee_country)
    redis_indexname_info = 'shopee_data_info_{}'.format(Shopee_country)

    domain = domain_list[Shopee_country]

    yuandata = commonRedisClass.redisbpop(flag=0, redisKeyName=redis_indexname, redisType=1)[1]  # 获取redis链接任务

    yuandata_dict = json.loads(yuandata)
    print(type(yuandata_dict),yuandata_dict)
    itemid = yuandata_dict[1]
    shopid = yuandata_dict[2]
    sales31_list = yuandata_dict[3]

    headers = {
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
        'x-api-source': "pc",
        'x-requested-with': "XMLHttpRequest"
    }

    headers['TARGETURL'] = 'https://{}/api/v2/item/get?itemid={}&shopid={}'.format(domain, itemid, shopid)
    # headers['user-agent'] = userAgent.getPc()
    headers['if-none-match-'] = "55b03-" + get_md5(
        '55b03' + get_md5('itemid={}&shopid={}'.format(itemid, shopid)) + "55b03")
    url = 'https://{}/a-i.{}.{}'.format(domain_list[Shopee_country], shopid, itemid)
    headers['referer'] = url
    needmd5 = "55b03-" + get_md5('55b03' + get_md5('itemid={}&shopid={}'.format(itemid, shopid)) + "55b03")
    headers['if-none-match-'] = needmd5
    headers['referer'] = 'https://{}/a-i.{}.{}'.format(domain, shopid, itemid)
    headers['TARGETURL'] = 'https://{}/api/v2/item/get?itemid={}&shopid={}'.format(
        domain, itemid, shopid)

    try:
        for useType in '3330133':
            headers['USETYPE'] = useType
            poxy_url = "http://sz-listing-dynamic-proxy.eccang.com"
            response = requests.get(poxy_url, headers=headers, timeout=5)
            data = json.loads(response.text)
            item = data['item']
            if item == None:  #
                print('平台下架的url')
                print('https://{}/a-i.{}.{}'.format(domain, shopid, itemid))
                commonRedisClass.redispush(flag=0, redisKeyName=redis_indexname_del, data=json.dumps(yuandata),
                                                redisType=1)

                return

            else:
                es_data = setResult(response.text, url, Shopee_country)
                now_sold = es_data['base']['sales']

                len_sale31 = len(sales31_list)
                print(sales31_list)
                if len_sale31 < 31:
                    sales31_list.append(now_sold)
                else:
                    del sales31_list[0]
                    sales31_list.append(now_sold)
                es_data['base']['sales_bag'] = get_sales(sales31_list)
                es_data['sales31'] = sales31_list
                redis_data = {
                    "es_id": '{}_{}'.format(itemid, shopid),
                    "es_data": es_data
                }
                # 推到redis
                commonRedisClass.redispush(flag=0, redisKeyName=redis_indexname_info, data=json.dumps(redis_data),
                                                redisType=1)
                print('add+1')
                return
    except Exception as e:
        print('erro:', e)
        commonRedisClass.redispush(flag=0, redisKeyName=redis_indexname, data=yuandata, redisType=1)
        print(e)
    return

if __name__ == '__main__':
    while True:
        execMain()