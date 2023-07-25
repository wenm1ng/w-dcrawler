#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import sys,os

import elasticsearch
import redis

o_path = os.getcwd()
sys.path.append(o_path)

from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis
from App.common.funs import getFirstRightValueByMark

def execMain():
    commonRedisClass = commonRedis()
    commonElasticSearchClass = commonElasticSearch()

    Shopee_country = getFirstRightValueByMark(matchString=os.path.dirname(__file__), mark=os.sep)

    redis_indexname_info = 'shopee_data_info_{}'.format(Shopee_country)
    es_indexname = "shopee_info_{}".format(Shopee_country)

    try:
        redis_data = commonRedisClass.redisbpop( flag=1, redisKeyName=redis_indexname_info,
                                        redisType=1)[1]  # 获取redis链接任务
        try:
            redis_data_dict = json.loads(redis_data)
            es_id = redis_data_dict['es_id']
            es_data = redis_data_dict['es_data']
            q = commonElasticSearchClass.insertDataByIndexKey(index=es_indexname,
                                                                   doc_type="_doc", id=es_id, data=es_data,
                                                                   elasticsearchType=1)
            print(q)
        except elasticsearch.exceptions.TransportError as e:
            commonRedisClass.redispush(1, redisKeyName=redis_indexname_info, data=json.dumps(redis_data),
                                            redisType=1)

    except redis.exceptions.ConnectionError as e:
        print(e)

if __name__ == '__main__':
    while True:
        execMain()