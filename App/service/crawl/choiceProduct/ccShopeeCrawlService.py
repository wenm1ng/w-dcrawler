# coding: utf-8
import hashlib
import random
from urllib import parse
import json

import math
import requests
from App.controller.baseController import baseController
from App.service.system.classContextService import classContextService
from Configs import defaultApp
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch

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

sortFieldmapping = {
    '': '?by=relevancy',
    'ctime': '?by=ctime',
    'price': '?by=',
    'sales': "?by=sales"

}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1'
}


def get_md5(str):
    strmd5 = hashlib.md5(str.encode(encoding='UTF-8')).hexdigest()
    return strmd5


class ccShopeeCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Shopee'

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

    def getClouldList(self):
        commonElasticSearchClass = commonElasticSearch()
        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')

        keyword = jsonParams.get('keyword', '')

        country = jsonParams.get('country', 'th')

        keyword2 = str(parse.quote(keyword.encode()))  # 解析关键词

        realurl = 'https://{domain}/search?keyword={str_parkw}'.format(domain=domain_list[country],
                                                                       str_parkw=keyword2)

        url = 'https://{domain}/api/v4/search/search_items'.format(domain=domain_list[country])

        sortField = jsonParams.get('sortField', '')  # 默认平台销量 sales sales3 sales7 sales15 sales30
        if sortField == "":
            url = url + '?by=relevancy'
        else:
            sort_type = '?by={}'.format(sortField)
            url = url + str(sort_type)

        keyword = jsonParams.get('keyword', '')
        if keyword == "":
            pass
        else:
            url = url + '&keyword={}'.format(keyword2)

        pageSize = jsonParams.get('pageSize', '50')
        if int(pageSize) <= 50:
            url = url + '&limit={}'.format(pageSize)
        else:
            url = url + '&limit=50'

        prePage = jsonParams.get('prePage', '1')
        if int(prePage) <= 1:
            url = url + '&newest=0'
        else:
            url = url + '&newest={}'.format((int(prePage) - 1) * int(pageSize))

        sort = jsonParams.get('sort', '1')
        if sort == "":
            url = url +'&order=desc'
        else:
            url = url + '&order={}'.format(sort)


        rangeFrom = jsonParams.get('rangeFrom', '')
        rangeTo = jsonParams.get('rangeTo', '')
        if rangeFrom == "" and rangeTo == "":
            pass
        elif rangeFrom != "" and rangeTo == "":
            url = url + '&price_min={}'.format(rangeFrom)
        elif rangeFrom == "" and rangeTo != "":
            url = url + '&price_max={}'.format(rangeFrom)
        else:
            url = url + '&price_min={}'.format(rangeFrom) + '&price_max={}'.format(rangeTo)


        url = url + '&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2'
        print(url)

        categoryIds = []
        for i in '333':
            try:
                headers['if-none-match-'] = "55b03-" + get_md5(
                    '55b03' + get_md5(domain_list[country] + '/search') + "55b03")
                headers['referer'] = realurl
                headers['USETYPE'] = i
                headers['TARGETURL'] = url
                resp = requests.get(defaultApp.szListingDynamicProxyUrl, headers=headers, timeout=5)
                datas = json.loads(resp.text)
                result = {
                    "msg": "recevied",
                    "code": 200,
                    "result": {
                        "data": []
                    }
                }

                for i in datas['items']:
                    img_src = 'https://cf.{domain}/file/{img}_tn'.format(domain=domain_list[country],
                                                                         img=i['item_basic']['image'])
                    if country == 'tw':
                        img_src = 'https://s-cf-tw.shopeesz.com/file/{img}_tn'.format(domain=domain_list[country],
                                                                         img=i['item_basic']['image'])
                    title = i['item_basic']['name']
                    item_id = i['item_basic']['itemid']
                    mall_id = i['item_basic']['shopid']
                    src_url = 'https://{domain}/a-i.{mall_id}.{item_id}'.format(domain=domain_list[country], mall_id=mall_id,
                                                                                item_id=item_id)
                    category_id = i['item_basic']['catid']
                    # category_name = i['category_name']
                    price = i['item_basic']['price'] / 100000
                    total_sold = i['item_basic']['historical_sold']
                    rate = i['item_basic']['item_rating']['rating_star']
                    ship_from_location = i['item_basic']['shop_location']
                    ee = {
                        "img_src": str(img_src),
                        "title": str(title),
                        "item_id": str(item_id),
                        "mall_id": str(mall_id),
                        "src_url": str(src_url),
                        "category_id": str(category_id),
                        "category_name": str(category_id),
                        "price": str(format(price, '.2f')),
                        "total_sold": str(total_sold),
                        "rate": format(rate, '.2f'),
                        "sku_num": "-",
                        "ship_from_location": ship_from_location,
                        "real_post_fee": "-",  # 是否包邮
                        "shipping_price": "-",
                        "platform":'shopee'
                    }
                    categoryIds.append(str(category_id))
                    result['result']['data'].append(ee)

                data_count = datas['total_count']
                result['total'] = int(data_count)
                total_pages = math.ceil(int(data_count) / int(pageSize))
                if total_pages >= 100:
                    result['total_pages'] = 100
                else:
                    result['total_pages'] = total_pages

                result['pages_size'] = int(pageSize)

                # categoryIds = list(set(categoryIds))
                # print(categoryIds)
                # KQLdata = {
                #     "query": {
                #         "bool": {
                #             "must": [{
                #                 "terms": {
                #                     "category_id": categoryIds
                #                 }
                #             }],
                #         }
                #     },
                # }
                # countryMap = {
                #     'th': 'shopee_category_th',
                #     'my': 'shopee_category_my',
                #     'id': 'shopee_category_id',
                #     'vn': 'shopee_category_vn',
                #     'br': 'shopee_category_br',
                #     'sg': 'shopee_category_sg',
                #     'ph': 'shopee_category_ph'
                # }
                # print(KQLdata)
                # es_data = commonElasticSearchClass.getByEsSearch(index=countryMap[country], KQLdata=KQLdata,
                #                                                  elasticsearchType=1)
                #
                # categoryMap = {}
                # hits = es_data['hits']['hits']
                # if hits:
                #     for es_data_i in hits:
                #         if '_source' not in es_data_i:
                #             break
                #         esDataSource = es_data_i['_source']
                #         categoryMap[esDataSource['category_id']] = esDataSource['category_name_local']
                #
                # for resultDataIndex in result['result']['data']:
                #     if resultDataIndex['category_id'] in categoryMap.keys():
                #         resultDataIndex['category_name'] = categoryMap[resultDataIndex['category_id']]
                return result
            except Exception as e:
                print(333,e)
                continue

        return '查询超时'


    def getInfo(self):
        return

    def getItemLoc(self):
        return

    def getParentCategoryId(self):
        return

    def getInforMation(self):
        return
