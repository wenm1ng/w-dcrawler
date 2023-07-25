#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys, os
import re, os, json, time
import datetime

o_path = os.getcwd()
sys.path.append(o_path)

from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.funs import getFirstRightValueByMark

def execMain():
    commonRedisClass = commonRedis()
    commonElasticSearchClass = commonElasticSearch()

    Shopee_country = getFirstRightValueByMark(matchString=os.path.dirname(__file__), mark=os.sep)
    redis_indexname = "shopee_url_{}".format(Shopee_country)
    es_indexname = "shopee_info_{}".format(Shopee_country)

    day_time = int(time.mktime(datetime.date.today().timetuple()))

    searchAfterList = []
    # 查询零点当天0点前且销量大于1
    query = {
        "query": {
            "bool": {
                "must": [],
                "filter": [
                    {
                        "match_all": {}
                    },
                    {
                        "range": {
                            "update_timestamp": {
                                "gte": None,
                                "lt": day_time
                            }
                        }
                    },
                    {
                        "range":
                            {
                                "base.sales":
                                    {
                                        "gte": 1,
                                        "lt": None
                                    }
                            }
                    }
                ],
                "should": [],
                "must_not": []
            }
        },
        "sort": [
            {"base.productId": {"order": "asc"}},
            {"base.mall_id": {"order": "asc"}}
        ],
        "_source": [
            "base.productId",
            "base.mall_id",
            "sales31"
        ]
    }

    searchAfterListString = commonRedisClass.getHashDataByKey(redisKeyName='getEsSalesDataPushRedis', key=redis_indexname,redisType=1)
    if searchAfterListString:
        searchAfterList = searchAfterListString.split(',')
        if searchAfterList:
            query['search_after'] = searchAfterList

    commonRedisClass.setPipeline(redisType=1)
    for index in range(100000):
        sortString = ''
        query['size'] = 1000
        print(query)
        page = commonElasticSearchClass.getByEsSearch(index=es_indexname, KQLdata=query, elasticsearchType=1)
        datas = page['hits']['hits']
        if not datas:
            print('无数据')
            break
        for data_i in datas:
            info = data_i['_source']
            itemid = info['base']['productId']
            mall_id = info['base']['mall_id']
            sales31 = info['sales31']
            yuandata = [0, itemid, mall_id, sales31]
            # print(yuandata)
            sortString = str(data_i['sort'][0]) + ',' + str(data_i['sort'][1])
            commonRedisClass.redispush(flag=0, redisKeyName=redis_indexname, data=json.dumps(yuandata), redisType=1)
        commonRedisClass.setHashDataByKey(redisKeyName='getEsSalesDataPushRedis', key=redis_indexname, value=sortString,redisType=1)

        if sortString:
            searchAfterList = sortString.split(',')
            if searchAfterList:
                query['search_after'] = searchAfterList


if __name__ == '__main__':
    execMain()
