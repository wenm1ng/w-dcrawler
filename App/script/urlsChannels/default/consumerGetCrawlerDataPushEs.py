#!/usr/bin/python
# -*- coding:utf-8 -*-
import json,sys, os,time,datetime

import elasticsearch
import redis

o_path = os.getcwd()
sys.path.append(o_path)

from App.service.crawl.relayService import relayService
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.funs import getFirstRightValueByMark
from App import app


def execMain():
    # time.sleep(0.5)
    commonRedisClass = commonRedis()
    currentType = getFirstRightValueByMark(matchString=os.path.dirname(__file__), mark=os.sep)
    redis_indexname_info = 'urlsChannels_info_{}'.format(currentType)
    redis_error_indexname_info = 'urlsChannels_error_info_{}'.format(currentType)

    redis_data = commonRedisClass.getRpopListDataByKey(redisKeyName=redis_indexname_info)
    if not redis_data:
        return

    try:
        jsonParams = json.loads(redis_data)
        print(jsonParams)
        print(type(jsonParams))
        relayBaseService = relayService()
        productCenterExtInfo = {
            'companyCode': '',
            'userId': '0',
        }
        if 'companyCode' in jsonParams and 'userId' in jsonParams:
            productCenterExtInfo = {
                'companyCode': jsonParams['companyCode'],
                'userId': str(jsonParams['userId']),
            }

        relayBaseService.setRouterMapKey('urls')
        relayBaseService.setUrls(jsonParams['link_list'])
        relayBaseService.setProductCenterExtInfo(productCenterExtInfo)
        relayBaseService.getResult()
    except Exception as e:
        print(e)
        commonRedisClass.redispush(1, redisKeyName=redis_error_indexname_info, data=redis_data)


if __name__ == '__main__':
    while True:
        with app.app_context():
            execMain()
