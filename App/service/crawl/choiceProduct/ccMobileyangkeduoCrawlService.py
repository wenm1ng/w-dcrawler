# coding: utf-8
import json
import random
import re, os.path, time, urllib.parse

import math
from App.service.system.logService import logService

from App.controller.baseController import baseController
from App.service.system.classContextService import classContextService
from Configs import defaultApp

'''
 # 66ip
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''

from pddsdk.client import Client

client_id = defaultApp.pdd_client_id
client_secret = defaultApp.pdd_client_secret
pdd_pid_mapping = defaultApp.pdd_pid_mapping




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

    def getClouldList(self):
        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        pdd_api_params = {
            'type': 'pdd.ddk.goods.search',
            'pid': pdd_pid_mapping['pdd_pid'],
            'custom_parameters': pdd_pid_mapping['pdd_custom_parameters']
        }

        catId = jsonParams.get('catId', [])
        if catId == []:
            pass
        else:
            pdd_api_params.update({'cat_id': str(catId[-1])})

        keyword = jsonParams.get('keyword', '')
        if keyword == "":
            pass
        else:
            pdd_api_params.update({'keyword': str(keyword)})

        pageSize = jsonParams.get('pageSize', '50')
        if int(pageSize) <= 50:
            pdd_api_params.update({'page_size': int(pageSize)})
        else:
            pdd_api_params.update({'page_size': 50})

        prePage = jsonParams.get('prePage', '1')
        if int(prePage) <= 0:
            pdd_api_params.update({'page': int(1)})
        else:
            pdd_api_params.update({'page': int(prePage)})

        range_list = []

        # 价格
        rangeFrom = jsonParams.get('rangeFrom', '')
        rangeTo = jsonParams.get('rangeTo', '')
        if rangeFrom == "" and rangeTo == "":
            pass
        elif rangeFrom != "" and rangeTo == "":
            range_list.append({"range_id": int(1), "range_from": int(rangeFrom)*100})
        elif rangeFrom == "" and rangeTo != "":
            range_list.append({"range_id": int(1), "range_to": int(rangeTo)*100})
        else:
            range_list.append({"range_id": int(1), "range_from": int(rangeFrom)*100, "range_to": int(rangeTo)*100})
        # 销量
        soldFrom = jsonParams.get('soldFrom', '')
        soldTo = jsonParams.get('soldTo', '')
        if soldFrom == "" and soldTo == "":
            pass
        elif soldFrom != "" and soldTo == "":
            range_list.append({"range_id": int(5), "range_from": int(soldFrom)*100})
        elif soldFrom == "" and soldTo != "":
            range_list.append({"range_id": int(5), "range_from": int(soldTo)*100})
        else:
            range_list.append({"range_id": int(5), "range_from": int(soldFrom)*100, "range_to": int(soldTo)*100})

        if range_list == []:
            pass
        else:
            pdd_api_params.update({'range_list': json.dumps(range_list)})

        sortField = jsonParams.get('sortField', '')  # 默认平台销量 sales sales3 sales7 sales15 sales30
        if sortField == "":
            pdd_api_params.update({'sort_type': 0})
        else:
            sort_type_mapping = {
                "price": {
                    "asc": 3,
                    "desc": 4
                },
                "sales": {
                    "asc": 5,
                    "desc": 6
                }
            }

            sort = jsonParams.get('sort', '')
            if sort == "":
                pass
            else:
                sort_type = sort_type_mapping[sortField][sort]
                pdd_api_params.update({'sort_type': sort_type})

        has_coupon = jsonParams.get('has_coupon', 'false')
        if has_coupon != "":
            pdd_api_params.update({'has_coupon': has_coupon})

        pdd_api_params.update({'use_customized': 'false'})

        print(json.dumps(pdd_api_params))
        resp = Client(client_id, client_secret).call(pdd_api_params)
        print(json.dumps(resp))
        result = {
            "msg": "recevied",
            "code": 200,
            "result": {
                "data": []
            }
        }

        for i in resp['goods_search_response']['goods_list']:
            img_src = i['goods_thumbnail_url']
            title = i['goods_name']
            item_id = i['goods_id']
            mall_id = i['mall_id']
            src_url = 'https://mobile.yangkeduo.com/goods.html?goods_id='+ str(item_id)
            category_id = i['category_id']
            category_name = i['category_name']
            price = i['min_group_price']
            total_sold = i['sales_tip']

            ee = {
                "img_src": str(img_src),
                "title": str(title),
                "item_id": str(item_id),
                "mall_id": str(mall_id),
                "src_url": str(src_url),
                "category_id": str(category_id),
                "category_name": str(category_name),
                "price": str(format(float(price)/100,'.2f')),
                "total_sold": str(total_sold),
                "rate": "-",
                "sku_num": "-",
                "ship_from_location": "-",
                "real_post_fee": "-",  # 是否包邮
                "shipping_price": "-",
                "platform": 'pdd'
            }
            result['result']['data'].append(ee)

        data_count = resp['goods_search_response']['total_count']
        result['total'] = int(data_count)
        result['total_pages'] = math.ceil(int(data_count) / int(pageSize))
        result['pages_size'] = int(pageSize)

        return result

    def getInfo(self):
        return

    def getItemLoc(self):
        return

    def getParentCategoryId(self):
        return

    def getInforMation(self):
        return
