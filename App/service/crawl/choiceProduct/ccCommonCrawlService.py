# coding: utf-8
import hashlib
import random
from urllib import parse
import json

import math
import requests

from App.controller.baseController import baseController
from App.service.system.classContextService import classContextService
from App.model.crawl.channels.commonElasticSearch import commonElasticSearch

domain_map = {
    'th': 'shopee.co.th',
    'sg': 'shopee.sg',
    'id': 'shopee.co.id',
    'my': 'shopee.com.my',
    'vn': 'shopee.vn',
    'ph': 'shopee.ph',
    'tw': 'xiapi.xiapibuy.com',
    'br': 'shopee.com.br'
}

category_type_map = {
    'shopee': {
        'th': 'shopee_category_th',
        'my': 'shopee_category_my',
        'id': 'shopee_category_id',
        'vn': 'shopee_category_vn',
        'br': 'shopee_category_br',
        'sg': 'shopee_category_sg',
        'ph': 'shopee_category_ph',
        'tw': 'shopee_category_tw'
    },
    'taobao': 'taobao_info',
    'pdd': 'pdd_info'
}

type_map = {
    'shopee': {
        'th': 'shopee_info_th',
        'my': 'shopee_info_my',
        'id': 'shopee_info_id',
        'vn': 'shopee_info_vn',
        'sg': 'shopee_info_sg',
        'tw': 'shopee_info_tw',
        'br': 'shopee_info_br',
        'ph': 'shopee_info_ph',
    },
    'taobao': 'taobao_info',
    'pdd': 'pdd_info'
}


class ccCommonCrawlService(object):
    """
    # 对象
    # @var string
    """
    relayServiceClass = {}

    """
    # 采集渠道名称
    # @var string
    """
    channleName = 'Common'

    """
     # 设置对象
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月12日 15:56:10
    """

    commonElasticSearchClass = commonElasticSearch()

    def setRelayServiceClass(self, relayServiceClass):
        if not relayServiceClass:
            return False
        if not self.relayServiceClass:
            self.relayServiceClass = relayServiceClass

    def getCategory(self):
        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        print(jsonParams)

        KQLdata = {
            "size": 500,
            "query": {
                "bool": {
                    "must": []
                }
            },
            "sort": [
                {
                    "category_id": {
                        "order": "asc"
                    }
                }
            ]
        }

        platform = jsonParams.get('platform', 'shopee')  # 默认SHOPEE  PDD   TAOBAO
        if platform == "shopee":
            country = jsonParams.get('country', 'th')  # shopee 平台默认泰国
        else:
            country = jsonParams.get('country', '')  # 默认shopee

        pid = jsonParams.get('pid', "0")
        if str(pid):
            KQLdata['query']['bool']['must'].append(
                {
                    "term": {
                        "parent_id": str(pid)
                    }
                }
            )

        es_cc_index = category_type_map[platform][country]

        print(json.dumps(KQLdata))
        es_data = self.commonElasticSearchClass.getByEsSearch(index=es_cc_index, KQLdata=KQLdata, elasticsearchType=1)

        # hits = es_data['hits']['hits']

        result = {
            "msg": "recevied",
            "code": 200,
            "result": {
                "data": []
            }
        }
        if not es_data:
            return result
        hits = es_data['hits']['hits']
        for es_data_i in hits:
            result['result']['data'].append(es_data_i['_source'])

        return result

    def getClouldList(self):
        return

    def getLocalList(self):
        platformDatabase = 0
        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        print(json.dumps(jsonParams))

        KQLdata = {
            "query": {
                "bool": {
                    "must": [],
                    "filter": [],
                    "should": [],
                    "must_not": []
                }
            },
            "sort": [],
            "_source": [
                # "base.sales",
                # "base.productId",
                # "base.mall_id",
                # "base.sales_bag"
            ]
        }
        platform = jsonParams.get('platform', 'shopee')  # 默认SHOPEE  PDD   TAOBAO
        # print(platform)
        if platform == "shopee":
            country = jsonParams.get('country', 'th')  # shopee 平台默认泰国
            es_index = type_map[platform][country]

        else:
            country = jsonParams.get('country', '')  # 默认shopee
            es_index = type_map[platform]

        catId = jsonParams.get('catId', [])
        if catId == []:
            pass
        else:
            creg_level = len(catId) - 1
            KQLdata['query']['bool']['must'].append(
                {
                    "term": {
                        "base.categories_bag.{}".format(creg_level): {
                            "value": catId[-1]
                        }
                    }
                }
            )

        keyword = jsonParams.get('keyword', '')
        if keyword == "":
            pass
        else:
            if platform in ['shopee']:

                KQLdata['query']['bool']['must'].append(
                    {
                        "match_phrase": {
                            "base.title_en": {
                                "query": "{}".format(keyword)
                            }
                        }
                    }
                )
            else:
                KQLdata['query']['bool']['must'].append(
                    {
                        "match_phrase": {
                            "base.title": {
                                "query": "{}".format(keyword)
                            }
                        }
                    }
                )

        pageSize = jsonParams.get('pageSize', '30')
        if int(pageSize) <= 50:
            KQLdata['size'] = pageSize
        else:
            KQLdata['size'] = 50

        prePage = jsonParams.get('prePage', '1')
        if int(prePage) <= 0:
            prePage = 1
        KQLdata['from'] = (int(prePage) - 1) * int(pageSize)

        soldFrom = jsonParams.get('soldFrom', '')
        soldTo = jsonParams.get('soldTo', '')
        # print(soldFrom, soldTo)
        if soldFrom == "" and soldTo == "":
            pass
        elif soldFrom != "" and soldTo == "":
            KQLdata['query']['bool']['filter'].append(
                {
                    "range": {
                        "base.sales": {
                            "gte": soldFrom,
                            "lt": None,
                        }
                    }
                }
            )
        elif soldFrom == "" and soldTo != "":
            KQLdata['query']['bool']['filter'].append(
                {
                    "range": {
                        "base.sales": {
                            "gte": None,
                            "lt": soldTo
                        }
                    }
                }
            )
        else:
            KQLdata['query']['bool']['filter'].append(
                {
                    "range": {
                        "base.sales": {
                            "gte": soldFrom,
                            "lt": soldTo
                        }
                    }
                }
            )
            pass

        rangeFrom = jsonParams.get('rangeFrom', '')
        rangeTo = jsonParams.get('rangeTo', '')
        # print(rangeFrom, rangeTo)
        if rangeFrom == "" and rangeTo == "":
            pass
        elif rangeFrom != "" and rangeTo == "":
            KQLdata['query']['bool']['filter'].append(
                {
                    "range": {
                        "base.price": {
                            "gte": rangeFrom,
                            "lt": None,
                        }
                    }
                }
            )
        elif rangeFrom == "" and rangeTo != "":
            KQLdata['query']['bool']['filter'].append(
                {
                    "range": {
                        "base.price": {
                            "gte": None,
                            "lt": rangeTo
                        }
                    }
                }
            )
        else:
            KQLdata['query']['bool']['filter'].append(
                {
                    "range": {
                        "base.price": {
                            "gte": rangeFrom,
                            "lt": rangeTo
                        }
                    }
                }
            )
            pass

        shipFromLocation = jsonParams.get('shipFromLocation', "")
        if shipFromLocation == "":
            pass
        else:
            KQLdata['query']['bool']['must'].append(
                {
                    "term": {
                        "base.location": shipFromLocation
                    }
                }
            )

        isFreeShopping = jsonParams.get('isFreeShopping', "")
        if isFreeShopping == "":
            pass
        else:
            KQLdata['query']['bool']['must'].append(
                {
                    "term": {
                        "base.delivery_bag.Free_shipping": shipFromLocation
                    }
                }
            )

        sortField = jsonParams.get('sortField', '')  # 默认平台销量 sales sales3 sales7 sales15 sales30
        if sortField == "":
            pass
        else:
            sortField_map = {
                "sales": "base.sales",
                "sales3": "base.sales_bag.three_day_sold",
                "sales7": "base.sales_bag.seven_day_sold",
                "sales15": "base.sales_bag.fifteen_day_sold",
                "price": "base.price",
                "sales30": "base.sales_bag.thirty_day_sold"
            }
            p_es_name = sortField_map[sortField]
            print(p_es_name)
            sort = jsonParams.get('sort', '')  # desc | asc
            if sort == "":
                pass
            else:
                KQLdata['sort'].append(
                    {
                        p_es_name: {
                            "order": sort
                        }
                    }
                )

        print(json.dumps(KQLdata))

        es_data = self.commonElasticSearchClass.getByEsSearch(index=es_index, KQLdata=KQLdata, elasticsearchType=1)


        result = {
            "msg": "recevied",
            "code": 200,
            "result": {
                "data": []
            }
        }

        if es_data:
            hits = es_data['hits']['hits']
            if hits:
                for es_data_i in hits:
                    if '_source' not in es_data_i:
                        break
                    esDataSource = es_data_i['_source']
                    # print(es_data_i)
                    img_src = esDataSource['image'] if 'https://' in esDataSource[
                        'image'] else "https://cf.{}/file/".format(domain_map[country]) + esDataSource['image']
                    title = esDataSource['base']['title_en']
                    item_id = esDataSource['base']['productId']
                    mall_id = esDataSource['base']['mall_id']
                    src_url = esDataSource['base']['sourceUrl']
                    price = esDataSource['base']['price']
                    category_id = esDataSource['base']['categories_bag']['0']
                    total_sold = esDataSource['base']['sales']
                    sold_3 = esDataSource['base']['sales_bag']['three_day_sold']
                    sold_7 = esDataSource['base']['sales_bag']['seven_day_sold']
                    sold_15 = esDataSource['base']['sales_bag']['fifteen_day_sold']
                    sold_30 = esDataSource['base']['sales_bag']['thirty_day_sold']
                    if sold_3 < 0:
                        sold_3 = 0
                    if sold_7 < 0:
                        sold_7 = 0
                    if sold_15 < 0:
                        sold_15 = 0
                    if sold_30 < 0:
                        sold_30 = 0
                    rate = 0.00
                    if 'product_rating' in esDataSource['base']:
                        if esDataSource['base']['product_rating']:
                            rate = float(esDataSource['base']['product_rating'])
                    sku_num = len(esDataSource['variableList'])
                    ship_from_location = esDataSource['base']['location']
                    ee = {
                        "img_src": img_src,
                        "title": title,
                        "item_id": item_id,
                        "mall_id": mall_id,
                        "src_url": src_url,
                        "category_id": category_id,
                        "price": float(price),
                        "total_sold": total_sold,
                        "sold_3": sold_3,
                        "sold_7": sold_7,
                        "sold_15": sold_15,
                        "sold_30": sold_30,
                        "rate": format(rate, ".2f"),
                        "sku_num": sku_num,
                        "ship_from_location": ship_from_location,
                        "real_post_fee": "-",
                        "shipping_price": "-",
                        "platform": platform
                    }
                    result['result']['data'].append(ee)

            del KQLdata['sort']
            del KQLdata['_source']
            del KQLdata['size']
            del KQLdata['from']
            es_data_count = \
                self.commonElasticSearchClass.getByEsCount(index=es_index, KQLdata=KQLdata, elasticsearchType=1)['count']

            result['total'] = int(es_data_count)
            result['total_pages'] = math.ceil(int(es_data_count) / int(pageSize))
            result['pages_size'] = int(pageSize)

        return result

    def getInfo(self):
        return

    def getItemLoc(self):
        return

    def getParentCategoryId(self):
        platformDatabase = 0
        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        print(json.dumps(jsonParams))
        KQLdata = {
            "query": {
                "bool": {
                    "must": [],
                    "must_not": []
                }
            },
            "size": 0
        }
        KQLdata['aggs'] = {
            "group_by_catid": {
                "terms": {
                    "field": "base.categories_bag.0",
                    "size": 2000
                }
            }
        }

        platform = jsonParams.get('platform', 'shopee')  # 默认SHOPEE  PDD   TAOBAO
        # print(platform)
        if platform == "shopee":
            country = jsonParams.get('country', 'th')  # shopee 平台默认泰国
            es_index = type_map[platform][country]
            es_cc_index = category_type_map[platform][country]
            platformDatabase = 1
        else:
            es_index = type_map[platform]
            es_cc_index = category_type_map[platform]
        print(json.dumps(KQLdata))

        es_data = self.commonElasticSearchClass.getByEsSearch(index=es_index, KQLdata=KQLdata, elasticsearchType=platformDatabase)
        aggs_buckets = es_data['aggregations']['group_by_catid']['buckets']
        print(aggs_buckets)

        data = {
            "msg": "recevied",
            "code": 200,
            "result": {}
        }

        for cc in aggs_buckets:
            print(cc)
            cid = cc['key']
            if cid == -1:
                continue
            total = cc['doc_count']
            es_cc_data = self.commonElasticSearchClass.getSourceByIndexKey(index=es_cc_index, id=cid,
                                                                           elasticsearchType=platformDatabase)
            if not es_cc_data:
                continue
            name = es_cc_data['category_name_local']

            data['result'].update(
                {
                    cid: {
                        "category_id": cid,
                        "pid": "0",
                        "name": name,  # 分类名
                        "total": int(total)
                    }
                }
            )

        # "11": {
        #     "category_id": "11",  # 分类id
        #     "pid": "0",
        #     "name": "电脑硬件/显示器/电脑周边",  # 分类名
        #     "catid_path": "11",  # 层级类目
        #     "child": [],
        #     "total": 30924  # 总数
        # }

        return data

    def getInforMation(self):
        return
