# coding: utf-8

import json, time, re
import base64
from App import app
from App.controller.baseController import baseController
from App.service.crawl.relayService import relayService
from Configs import defaultApp, site
from App.common.webRequest import WebRequest
from App.service.system.classContextService import classContextService
from App.common.model.baseRedis import baseRedis
from App.service.crawl.urlsChannels.ccAmazon2CrawlService import ccAmazonCrawlService
from App.common.MysqlPool import MysqlPool
from App.common.ossUpload import ossUpload

'''
 # 首页控制器
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class indexController(object):
    """
     # 欢迎页面
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """


    @app.route("/crwaling/amz", methods=['POST'])
    def getamzv(self=''):

        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')

        site = jsonParams['site']

        html  = ccAmazonCrawlService.saveHtmlResult(self,jsonParams)

        if html ==None:
            return '获取失败'
        else:
            need_data = ccAmazonCrawlService.setResult(self, site, html)

        return json.dumps(need_data)



    @app.route("/")
    def index(self=''):
        # a = 'https://data2.wago.io/search/es?q=expansion:sl type:weakaura tag:cl11&mode=wow&page=0&sort='
        # rs = re.match(r'.*?expansion:(.*?) type.*?tag:(.*?)&.*?', a)
        # print(rs.group(1))
        # print(rs.group(2))


        # table = 'wow_wa_content'
        # field = ['origin_title', 'origin_url', 'origin_description']
        # data = [{'origin_title': '采集测试1', 'origin_url': 'www.baidu.com', 'origin_description': '我是一个描述1'},{'origin_title': '采集测试1', 'origin_url': 'www.baidu.com', 'origin_description': '我是一个描述1'}]
        # row = MysqlPool().batch_insert(table, field, data)

        table = 'wow_wa_tab_title'
        field = '*'
        where = {'=': {'id': 2}}
        row = MysqlPool().first(table, where, field)
        print(row)
        # print(row)
        # time.sleep(2)

        # 测试千牛云图片
        # a = 'https://image6.coupangcdn.com/image/vendor_inventory/a8d3/e83a09715c57d72e8d2e47ed2e885dec74d78367e32223d2ac1927e6f152.PNG'
        # b = 'https://tpc.googlesyndication.com/simgad/1575545668792393300?sqp=4sqPyQQ7QjkqNxABHQAAtEIgASgBMAk4A0DwkwlYAWBfcAKAAQGIAQGdAQAAgD-oAQGwAYCt4gS4AV_FAS2ynT4&rs=AOga4qkum_Q2iWaHC7OnV-bmqEsCud5Uxw'
        # a = ossUpload().uploadImageQiNiu(b)
        # print(a)
        return "this is lscrawler."


    """
     # 爬虫采集接口
     # @param self
     # @return string
     # @author     WenMing
     # @createTime 2022年5月11日 15:22:56
    """

    @app.route("/api/getResultByUrls", methods=['GET', 'POST'])
    def getResultByUrls(self=''):
        try:
            jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
            print(jsonParams)
            relayBaseService = relayService()

            relayBaseService.setUrls(jsonParams['link_list'])
            urls = classContextService().getVarByName(name='relayService_urls')
            if not defaultApp.isUrlsChannelsAsynchrTask:
                relayBaseService.setRouterMapKey('urls')
                productCenterExtInfo = {
                    'companyCode': '',
                    'userId': '0',
                }
                if 'companyCode' in jsonParams and 'userId' in jsonParams:
                    productCenterExtInfo = {
                        'companyCode': jsonParams['companyCode'],
                        'userId': str(jsonParams['userId']),
                    }
                relayBaseService.setProductCenterExtInfo(productCenterExtInfo)
                relayBaseService.getResult()
            else:
                relayBaseService.setDefaultUrlsChannelsAsynchrTask(jsonParams=jsonParams)

            baseController().setSuccessCode()
            baseController().setApiResultData(True)
            baseController().setApiResultMsg('采集成功')
        except Exception as e:
            print('error file:'+e.__traceback__.tb_frame.f_globals["__file__"]+'_line:'+str(e.__traceback__.tb_lineno)+'_msg:'+str(e))  # 发生异常所在的文件
            baseController().setFailCode()
            baseController().setApiResultData(False)
            baseController().setApiResultMsg(str(e))
        return baseController().outputJson()

    """
         # 爬虫详情链接检查接口
         # @param self
         # @return string
         # @author     WenMing    736038880@qq.com
         # @createTime 2021年1月8日 15:22:56
        """
    @app.route("/check/url", methods=['GET', 'POST'])
    def checkUrls(self=''):
        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')

        true_list = []
        false_list = []
        for url in jsonParams['link_list']:

            if 'detail.1688.com/offer' in url:
                true_list.append(url)

            elif 'amazon'in url and '/dp/' in url:
                true_list.append(url)

            elif 'www.ebay'in url and '/itm/' in url:
                true_list.append(url)
            elif 'www.ebay'in url and  '/p/' in url:
                true_list.append(url)

            elif 'item.jd.com/'in url:
                true_list.append(url)

            elif 'aliexpress.com'in url and '/item/' in url:
                true_list.append(url)

            elif 'yangkeduo.com'in url and 'goods_id=' in url:
                true_list.append(url)

            elif 'pinduoduo.com/'in url and 'gid=' in url:
                true_list.append(url)

            elif 'lazada.com'in url and '/products/' in url:
                true_list.append(url)

            elif 'tmall'in url and 'id=' in url or '/item/' in url:
                true_list.append(url)

            elif 'taobao.com'in url and 'id=' in url and 'item' in url:
                true_list.append(url)

            elif 'www.joom.com'in url and 'products' in url:
                true_list.append(url)

            elif 'www.coupang.com'in url and 'products' in url:
                true_list.append(url)

            elif 'www.vvic.com/item/'in url:
                true_list.append(url)

            elif 'www.bao66.cn/p'in url:
                true_list.append(url)

            elif 'shopee'in url and '-i.' in url:
                true_list.append(url)

            elif 'shopee'in url and 'product' in url:
                true_list.append(url)

            elif 'walmart'in url and '/ip/' in url:
                true_list.append(url)
            elif 'xiapibuy.com'in url and  'search?' not in url:
                true_list.append(url)
            else:
                false_list.append(url)

        data = {
            "successs_list": true_list,
            "fail_list": false_list,
        }
        baseController().setSuccessCode()
        baseController().setApiResultData(data)
        baseController().setApiResultMsg('采集成功')
        return baseController().outputJson()

    """
     # 爬虫采集接口
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月8日 15:22:56
    """

    @app.route("/crwaling/Info", methods=['GET', 'POST'])
    def getJsonResultByUrls(self=''):
        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        relayBaseService = relayService()
        relayBaseService.setRouterMapKey('urls')
        relayBaseService.setUrls(jsonParams['data'])
        relayBaseService.setUrlsType(1)
        relayBaseService.getResult()
        baseController().setSuccessCode()
        baseController().setApiResultData(relayBaseService.getProductCenterInfo(relayBaseService.getJsonData(),type=jsonParams['type']))        # baseController().setApiResultData((relayBaseService.getJsonData()))
        baseController().setApiResultMsg('采集成功')
        return baseController().outputJson()

    @app.route("/api/getRealTimeResult", methods=['GET', 'POST'])
    def getRealTimeResult(self=''):
        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        relayBaseService = relayService()
        relayBaseService.setRouterMapKey('urls')
        relayBaseService.setUrls(jsonParams['link_list'])
        relayBaseService.setUrlsType(1)
        relayBaseService.getResult()
        baseController().setSuccessCode()
        baseController().setApiResultData(relayBaseService.getJsonData())        # baseController().setApiResultData((relayBaseService.getJsonData()))
        baseController().setApiResultMsg('采集成功')
        return baseController().outputJson()

    @app.route("/api/getCanCrawlerPlatform", methods=['GET', 'POST'])
    def getCanCrawlerPlatformSite(self=''):
        sites = site.briefSite
        baseController().setSuccessCode()
        baseController().setApiResultData(sites)
        baseController().setApiResultMsg('success')
        return baseController().outputJson()


    @app.route("/api/setPddToken", methods=['POST', ])
    def AcceptPddClient(self=''):
        PddData = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        baseController().setSuccessCode()
        baseController().setApiResultMsg('recevied')
        if 'data' in PddData:
            try:
                for itemList in PddData['data']:
                    token = itemList.split('~')[1]
                    baseRedis().connectRedis().zadd('pdd_client_mobile_token', {token: 0})
            except Exception as e:
                pass
        return baseController().outputJson()

    
    @app.route("/crwaling/GetCategory", methods=['GET', 'POST'])
    def getcategory(self=""):
        baseController().setSuccessCode()
        relayBaseService = relayService()
        relayBaseService.setRouterMapKey('choiceProduct')
        # platform = str(jsonParams.get('platform', ''))
        # relayBaseService.setChannel(platform)
        relayBaseService.setParamsType('0')
        result = relayBaseService.getOnlineChoicProductResult()
        # baseController().setSuccessCode()
        # baseController().setApiResultData(result)
        # baseController().setApiResultMsg('采集成功')
        # return baseController().outputJson(result)
        return json.dumps(result)

    @app.route("/crwaling/ClouldList", methods=['POST'])
    def getClouldList(self=''):
        # relayService().setUrls({})

        jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        relayBaseService = relayService()
        relayBaseService.setRouterMapKey('choiceProduct')
        platform = str(jsonParams.get('platform', ''))
        print(json.dumps(jsonParams))
        if platform == "":
            return '平台类型错误'

        platform_maping = {
            'pdd': 'Mobileyangkeduo',
            'taobao': 'Taobao',
            'shopee': 'Shopee'
        }
        relayBaseService.setChannel(platform_maping[platform])
        relayBaseService.setParamsType('1')
        result = relayBaseService.getOnlineChoicProductResult()

        return json.dumps(result)

    @app.route("/crwaling/LocalList", methods=['POST'])
    def getLocalList(self=''):
        # relayService().setUrls({})
        # jsonParams = classContextService().getVarByName(name=baseController().__class__.__name__ + '_jsonParams')
        baseController().setSuccessCode()
        relayBaseService = relayService()
        relayBaseService.setRouterMapKey('choiceProduct')
        # platform = str(jsonParams.get('platform', ''))
        # relayBaseService.setChannel(platform)
        relayBaseService.setParamsType('2')
        result = relayBaseService.getOnlineChoicProductResult()
        # baseController().setSuccessCode()
        # baseController().setApiResultData(result)
        # baseController().setApiResultMsg('采集成功')
        # return baseController().outputJson()
        return json.dumps(result)

    @app.route("/crwaling/ItemLoc", methods=['GET',"POST"])
    def geItemLoc(self=''):
        data = {
            "code":200,
            "msg":'',
            "result":{
                "group1": [
                    "北京",
                    "上海",
                    "广州",
                    "深圳",
                    "杭州,",
                    "海外",
                    "江浙沪",
                    "珠三角",
                    "京津冀",
                    "东三省",
                    "港澳台"
                ],
                "group2": [
                    "长沙",
                    "成都",
                    "大连",
                    "东给",
                    "佛山",
                    "福州",
                    "贵阳",
                    "合肥",
                    "金华",
                    "济南",
                    "嘉兴",
                    "昆明",
                    "宁波",
                    "南昌",
                    "南京",
                    "青岛",
                    "泉州",
                    "沈阳",
                    "苏州",
                    "天津",
                    "温州",
                    "无锡",
                    "武汉",
                    "西安",
                    "厦门",
                    "郑州",
                    "中山",
                    "石家庄",
                    "哈尔滨"
                ],
                "group3": [
                    "安徽",
                    "福建",
                    "甘肃",
                    "广东",
                    "广西",
                    "贵州",
                    "海南",
                    "河北",
                    "河南",
                    "湖北",
                    "湖南",
                    "江苏",
                    "江西",
                    "吉林",
                    "辽宁",
                    "宁夏",
                    "青海",
                    "山东",
                    "山西",
                    "陕西",
                    "云南",
                    "四川",
                    "西藏",
                    "新疆",
                    "浙江",
                    "澳门",
                    "香港",
                    "台湾",
                    "内蒙古",
                    "黑龙江"
                ]}
            }

        # data2 = {'code': 200, 'msg': '', 'result': data}
        # baseController().setSuccessCode()
        # baseController().setApiResultData(data)
        # baseController().setApiResultMsg('采集成功')
        # return baseController().outputJson()
        return json.dumps(data)

    @app.route("/crwaling/GetParentCategoryId", methods=['GET', 'POST'])
    def GetParentCategoryId(self=""):
        baseController().setSuccessCode()
        relayBaseService = relayService()
        relayBaseService.setRouterMapKey('choiceProduct')
        # platform = str(jsonParams.get('platform', ''))
        # relayBaseService.setChannel(platform)
        relayBaseService.setParamsType('5')
        result = relayBaseService.getOnlineChoicProductResult()
        # baseController().setSuccessCode()
        # baseController().setApiResultData(result)
        # baseController().setApiResultMsg('采集成功')
        # return baseController().outputJson()
        return json.dumps(result)


    @app.route("/cache/getUrlsChannelsError", methods=['GET'])
    def getUrlsChannelsError(self=""):
        from App.model.crawl.channels.commonRedis import commonRedis
        commonRedisClass = commonRedis()
        baseController().setSuccessCode()
        baseController().setApiResultData(commonRedisClass.getListDataByKey(redisKeyName='urlsChannels_error_info_default'))
        baseController().setApiResultMsg('查询成功')
        return baseController().outputJson()