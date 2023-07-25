#!/usr/bin/python
# -*- coding:utf-8 -*-

import sys, os
import redis
import re, os, json, time
import datetime, json
import math


# o_path = os.getcwd()
# sys.path.append(o_path)
#
# from App.model.crawl.channels.commonElasticSearch import commonElasticSearch
# from App.model.crawl.channels.commonRedis import commonRedis


def execMain():
    redisConfigList = [
        {
            'host': '',
            'port': 6379,
            'password': '',
            'decode_responses': True,
            'db': 14
        },
        {
            'host': '',
            'port': 6379,
            'password': '',
            'decode_responses': True,
            'db': 15
        }
    ]

    sourceRedisConnent = redis.Redis(**redisConfigList[0])
    targetRedisConnent = redis.Redis(**redisConfigList[1])

    sourceRedisKeys = sourceRedisConnent.keys()
    if not sourceRedisKeys:
        return

    for keysIndex in sourceRedisKeys:
        print(keysIndex)
        type = sourceRedisConnent.type(keysIndex)
        if type == 'list':
            keyCount = sourceRedisConnent.llen(keysIndex)
            if not keyCount:
                continue
            successionCount = math.ceil(keyCount / 5000)
            print(successionCount)
            for successionCountIndex in range(successionCount):
                rangeNum = 4999
                if not successionCountIndex:
                    indexStart = successionCountIndex
                    indexEnd = rangeNum
                else:
                    indexStart = indexEnd + 1
                    indexEnd = indexStart + rangeNum
                sourceRedisListData = sourceRedisConnent.lrange(keysIndex, indexStart, indexEnd)
                targetRedisPipeline = targetRedisConnent.pipeline()
                print('--------第:',successionCountIndex)
                for sourceIndex in sourceRedisListData:
                    targetRedisPipeline.lpush(keysIndex,sourceIndex)
                targetRedisPipeline.execute()
        print('ok')


if __name__ == '__main__':
    execMain()
