# coding: utf-8
import os

import redis
from Configs import redis as conRedis


class baseRedis(object):
    # connectPip = {}
    #
    # def __init__(self):
    #     self.connect_redis()

    def connectRedis(self,redisType=0):
        while True:
            try:
                redisCon = redis.Redis(**conRedis.RedisConfigList[redisType])
                redisCon.ping()
                return redisCon
            except Exception as e:
                print(e)
                print('redis连接失败,正在尝试重连')
                continue