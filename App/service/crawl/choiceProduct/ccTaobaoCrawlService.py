# -*- coding: utf-8 -*-
import math
import top as top
from App.controller.baseController import baseController
from App.service.system.classContextService import classContextService
from Configs import defaultApp

import json

req = top.api.TbkDgMaterialOptionalRequest()
req.set_app_info(top.appinfo(defaultApp.taobao_appkey, defaultApp.taobao_secret))
req.adzone_id = defaultApp.taobao_adzone_id



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


    def getClouldList(self):
        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        print(jsonParams)

        catId = jsonParams.get('catId', [])
        if catId == []:
            pass
        else:
            pass

        keyword = jsonParams.get('keyword', '')
        if keyword == "":
            pass
        else:
            req.q = str(keyword)

        pageSize = jsonParams.get('pageSize', '50')
        if int(pageSize) <= 50:
            req.page_size = pageSize
        else:
            req.page_size = 50

        prePage = jsonParams.get('prePage', '1')
        if int(prePage) <= 0:
            req.page_no = 1
        else:
            req.page_no = prePage

        rangeFrom = jsonParams.get('rangeFrom', '')
        rangeTo = jsonParams.get('rangeTo', '')
        if rangeFrom == "" and rangeTo == "":
            pass
        elif rangeFrom != "" and rangeTo == "":
            req.start_price = int(rangeFrom)
        elif rangeFrom == "" and rangeTo != "":
            req.end_price = int(rangeTo)
        else:
            req.start_price = int(rangeFrom)
            req.end_price = int(rangeTo)

        sortField = jsonParams.get('sortField', '')
        if sortField == "":
           pass
        else:
            sort_type_mapping ={
                'price':{
                    'asc':'price_asc',
                    'desc':'price_des'
                        },
                'sales':{
                    'asc': 'total_sales_asc',
                    'desc': 'total_sales_des'
                }
            }
            sort = jsonParams.get('sort', '')
            if sort == "":
                pass
            else:
                sort_type = sort_type_mapping[sortField][sort]
                req.sort = sort_type

        ship_from_location = jsonParams.get('shipFromLocation', '')
        if ship_from_location == "":
            pass
        else:
            req.itemloc = ship_from_location

        datas = req.getResponse()

        result = {
            "msg": "recevied",
            "code": 200,
            "result": {
                "data": []
            }
        }
        for i in datas['tbk_dg_material_optional_response']['result_list']['map_data']:
            # print(json.dumps(i))
            img_src = i['pict_url']
            title = i['title']
            item_id = i['item_id']
            mall_id = i['seller_id']
            src_url = i['item_url']
            category_id = i['category_id']
            category_name = i['category_name']
            price = i['zk_final_price']
            total_sold = i['tk_total_sales']
            ship_from_location = i['provcity']
            shipping_price = i['real_post_fee']
            if int(float(shipping_price)) == 0:
                real_post_fee = 'ture'
            else:
                real_post_fee = 'false'
            ee = {
                "img_src": str(img_src),
                "title": str(title),
                "item_id": str(item_id),
                "mall_id": str(mall_id),
                "src_url": str(src_url),
                "category_id": str(category_id),
                "category_name": str(category_name),
                "price": str(format(float(price), '.2f')),
                "total_sold": str(total_sold),
                "rate": "-",
                "sku_num": "-",
                "ship_from_location": ship_from_location,
                "shipping_price": shipping_price,
                "real_post_fee": real_post_fee,  # 是否包邮
                "platform": 'taobao'

            }
            result['result']['data'].append(ee)

        data_count = datas['tbk_dg_material_optional_response']['total_results']
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
