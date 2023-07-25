# -*- coding:utf-8 -*-
import requests,os,sys
import redis
import elasticsearch
import json

o_path = os.getcwd()
sys.path.append(o_path)

from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
from App.model.crawl.channels.commonRedis import commonRedis

def push_es(redis_data):
    commonElasticSearchClass = commonElasticSearch()
    redis_data_dict = json.loads(redis_data)
    es_id = redis_data_dict['es_id']
    es_data = redis_data_dict['es_data']
    q = commonElasticSearchClass.insertDataByIndexKey(index='coupang',
                                                      doc_type="_doc", id=es_id, data=es_data,
                                                      elasticsearchType=1)
    print(q)
    return


if __name__ == '__main__':
    commonRedisClass = commonRedis()
    while True:
        try:
            redis_data = commonRedisClass.redisbpop(flag=1, redisKeyName='coupang_es_data',redisType=1)[1]  # 获取redis链接任务
            try:
                push_es(redis_data)
            except elasticsearch.exceptions.TransportError as e:
                commonRedisClass.redispush(0, redisKeyName='coupang_es_data', data=redis_data,redisType=1)
                continue
        except redis.exceptions.ConnectionError as e:
            # print(e)
            continue
