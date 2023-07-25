# -*- coding:utf-8 -*-
import datetime
import time

import requests, os, sys
import redis

import random
import json
import hashlib
from lxml import etree

o_path = os.getcwd()
sys.path.append(o_path)

from App.common.userAgent import userAgent
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis


def get_md5(str):
    strmd5 = hashlib.md5(str.encode(encoding='UTF-8')).hexdigest()
    return strmd5


def del_itemid(yuandata):
    # 推送到删除队列
    redis_conn.lpush('url_{}_del'.format(Shopee_country), yuandata)
    return


def getcreg(categories):
    dataee = {}
    html = etree.HTML(categories)
    cid = html.xpath('//*[@id="breadcrumb"]/li/a/@href')
    name = html.xpath('//*[@id="breadcrumb"]/li/a/@title')
    for i, j in enumerate(tuple(zip(cid, name))):
        if i == 0:
            pass
        else:
            ee = {i - 1: j[0].replace('/np/categories/', '')}
            dataee.update(ee)
    return dataee


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


def setResult(sourceHtml, sourceHtml2, TARGETURL):
    s1 = json.loads(sourceHtml)

    data = {
        "base": {
            "productId": s1['productId'],
            "itemId": s1['itemId'],
            "vendorItemId": s1['vendorItemId'],
            "sourceUrl": TARGETURL,
            "categories_bag": getcreg(sourceHtml2),
            "sellerDetailInfo": s1['returnPolicyVo']['sellerDetailInfo']
        }
    }

    return data
    # desc_req = self.session.get(desc_url, headers=self.desc_headers, timeout=10)
    # result = self.parse_description(desc_req, product_data)
    # result_json = json.dumps(result)
    # sentinelServMaster.lpush(self.item_key, result_json)


def work():
    commonRedisClass = commonRedis()
    commonElasticSearchClass = commonElasticSearch()

    yuandata = commonRedisClass.redisbpop(flag=1, redisKeyName="coupang_url", redisType=1)[1]

    yuandata_dict = json.loads(yuandata)
    pf_id = yuandata_dict[1]
    item_id = yuandata_dict[2]
    vendorItemId = yuandata_dict[3]

    TARGETURL = 'https://www.coupang.com/vp/products/{}/items/{}/vendoritems/{}'.format(pf_id, item_id, vendorItemId)
    TARGETURL2 = 'https://www.coupang.com/vp/products/{}/breadcrumb-gnbmenu?&invalidProduct=false&invalidUnknownProduct=false&vendorItemId={}'.format(
        pf_id, vendorItemId)

    headers = {
        'x-api-source': "pc",
        'x-requested-with': "XMLHttpRequest",
        'TARGETURL': TARGETURL,
        'User-Agent': userAgent().getPc()
    }
    headers2 = {
        'x-api-source': "pc",
        'x-requested-with': "XMLHttpRequest",
        'TARGETURL': TARGETURL2,
        'User-Agent': userAgent().getPc()
    }

    for useType in '33333':
        try:
            headers['USETYPE'] = useType
            poxy_url = "http://sz-listing-dynamic-proxy.eccang.com"

            response = requests.get(poxy_url, headers=headers, timeout=5)

            response2 = requests.get(poxy_url, headers=headers2, timeout=5)
            if response.text == None or response2.text == None:
                print(11)
                return
            else:
                # print(TARGETURL)
                # print(response.text)
                # print('========='*6)
                # print(TARGETURL2)
                # print(response2.text)

                es_data = setResult(response.text, response2.text, TARGETURL)
                es_data = {
                    'es_id': pf_id,
                    'es_data': es_data
                }
                commonRedisClass.redispush(flag=0, redisKeyName='coupang_es_data', data=json.dumps(es_data),
                                           redisType=1)

                print('add+1')
                return
        except Exception as e:
            print('erro:', e)
            commonRedisClass.redispush(0, redisKeyName='coupang_url', data=json.dumps(yuandata),
                                       redisType=1)
            print(e)
            break
    return


if __name__ == '__main__':
    while True:
        work()
