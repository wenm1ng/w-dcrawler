# coding: utf-8
from App.common.model.baseRedis import baseRedis
from Configs import defaultApp
import json

'''
 # 设置代理池
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class distributedPoolInfomationRedis(object):
    """
     # 新增
     # @param self
     # @param 键名
     # @param 值
     # @return bool
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:35:07
    """

    def addListingProductHashDistributedPool(self, key, value):
        if not key:
            return False
        if not value:
            return False

        return baseRedis().connectRedis().hset(name=defaultApp.rancherProjectName, key=key, value=json.dumps(value))

    pass
