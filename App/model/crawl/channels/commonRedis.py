# coding: utf-8
from random import random, randint

from App.common.model.baseElasticsearch import baseElasticsearch
from App.common.model.baseRedis import baseRedis

from Configs import defaultApp
import json
import time

'''
 # 公共redis类
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class commonRedis(object):

    """
    # 对象
    # @var string
    """
    connectRedisClass = {}

    """
     # 获取数据
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:10:11
    """

    def getSourceByIndexKey(self, index, id, doc_type="_doc"):
        result = False
        data = baseElasticsearch.connectElasticsearch(self).get(index=index, doc_type=doc_type, id=id)
        if data:
            if '_source' in data.keys():
                if 'datajson' in data['_source'].keys():
                    result = data['_source']['datajson']
        return result


    """
     # 获取数据
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:10:11
    """

    def getStringByKey(self, redisKeyName, redisType=0):
        if not redisKeyName:
            return
        return self.getConnectRedis(redisType).get(redisKeyName)

    """
     # 获取数据
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:10:11
    """

    def setStringByKey(self, redisKeyName, value,exTime=14400,redisType=0):
        if not redisKeyName:
            return
        if not value:
            return
        return self.getConnectRedis(redisType).set(redisKeyName,value = value,  ex=exTime)


    """
     # 获取数据
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:10:11
    """

    def getListDataByKey(self, redisKeyName, indexStart=0, indexEnd=0,redisType=0):
        if not redisKeyName:
            return
        if indexStart == 0 and indexEnd == 0:
            indexEnd = -1
        return self.getConnectRedis(redisType).lrange(redisKeyName, indexStart, indexEnd)

    """
     # 获取数据
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:10:11
    """

    def getRpopListDataByKey(self, redisKeyName, redisType=0):
        if not redisKeyName:
            return

        return self.getConnectRedis(redisType).rpop(redisKeyName)

    """
     # 获取数据
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:10:11
    """

    def setHashDataByKey(self, redisKeyName,key, value,redisType=0):
        if not redisKeyName:
            return

        return self.getConnectRedis(redisType).hset(redisKeyName,key,value)

    """
     # 获取
     # @param redisType
     # @return object
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年6月10日 10:13:56
    """
    def getHashDataByKey(self, redisKeyName,key,redisType=0):
        if not redisKeyName:
            return

        return self.getConnectRedis(redisType).hget(redisKeyName,key)
    """
     # 获取数据
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年6月8日 18:52:45
    """

    def setPipeline(self,  redisType=0):
        return self.getConnectRedis(redisType).pipeline()


    """
     # 获取数据
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:10:11
    """

    def insertDataByIndexKey(self, redisKeyName, redisStr, redisType=0):
        self.getConnectRedis(redisType).zadd(redisKeyName, {redisStr: time.time()})
        return

    """
     # 自增1
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:10:11
    """

    def zincrbyValByKey(self, redisKeyName, value, redisType=0):
        result = False
        if not redisKeyName:
            return result
        if not value:
            return result
        return self.getConnectRedis(redisType).zincrby(redisKeyName, 1, value)

    """
     # 移除
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:28:01
    """

    def zremValByKey(self, redisKeyName, value, redisType=0):
        result = False
        if not redisKeyName:
            return result
        if not value:
            return result
        return self.getConnectRedis(redisType).zrem(redisKeyName, value)  # 移除

    """
     # 设置
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:28:01
    """

    def zscoreValByKey(self, redisKeyName, value, redisType=0):
        result = False
        if not redisKeyName:
            return result
        if not value:
            return result
        return self.getConnectRedis(redisType).zscore(redisKeyName, value)

    """
     # 获取长度
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:28:01
    """

    def zcardByKey(self, redisKeyName, redisType=0):
        result = 0
        if not redisKeyName:
            return result
        return self.getConnectRedis(redisType).zcard(redisKeyName)  # 获取cook池长度

    """
     # 获取默认区间
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:28:01
    """

    def zrevrangeByKey(self, redisKeyName, redisType=0):
        result = {}
        if not redisKeyName:
            return result
        return self.getConnectRedis(redisType).zrevrange(redisKeyName, 0, -1)

    """
     # 获取redis链接
     # @param redisType
     # @return object
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年6月10日 10:13:56
    """
    def getConnectRedis(self, redisType=0):
        if self.connectRedisClass:
            if redisType in self.connectRedisClass.keys():
                    try:
                        # print('------redis-cache--------')
                        # print(self.connectRedisClass[redisType])
                        # print('------redis-cache--------')
                        self.connectRedisClass[redisType].ping()
                        return self.connectRedisClass[redisType]
                    except Exception as e:
                        baseRedis.connectRedis(self, redisType).ping()
                        self.connectRedisClass[redisType] = baseRedis.connectRedis(self, redisType)
                        print('------redis-try-cache--------')
                        print(self.connectRedisClass[redisType])
                        print(e)
                        print('------redis-try-cache--------')
                        return self.connectRedisClass[redisType]


        self.connectRedisClass[redisType] = baseRedis.connectRedis(self, redisType)
        self.connectRedisClass[redisType].ping()
        # print('------redis-true--------')
        # print(self.connectRedisClass[redisType])
        # print('------redis-true--------')
        return self.connectRedisClass[redisType]


    def redisbpop(self, flag, redisKeyName, redisType=0):
        if flag == 0:
            return self.getConnectRedis(redisType).blpop(redisKeyName)
        elif flag == 1:
            return self.getConnectRedis(redisType).brpop(redisKeyName)
        else:
            return

    def redispush(self, flag, redisKeyName, data,redisType=0):
        if flag == 0:
            return self.getConnectRedis(redisType).lpush(redisKeyName,data)
        elif flag == 1:
            return self.getConnectRedis(redisType).rpush(redisKeyName,data)
        else:
            return

    def deleteRedisKey(self,redisKeyName,redisType=0):

        return self.getConnectRedis(redisType).rpush(redisKeyName)