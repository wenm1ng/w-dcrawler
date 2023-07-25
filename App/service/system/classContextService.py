# coding: utf-8
from flask import g
from App.common.funs import checkValueType

'''
 # 上下文管理
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月18日 09:25:06
 # @version     0.1.0 版本号
'''


class classContextService(object):
    """
     # 设置值
     # @param self
     # @param name string
     # @param value ? 值
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月18日 09:25:12
    """

    def setVarByNameValue(self, name, value):
        if not name:
            return False
        if not value:
            return False

        className = self.__class__.__name__

        if className:
            gName = className + '_' + name
        else:
            gName = name

        setattr(g, gName, value)

    """
     # 设置追加list
     # @param self
     # @param name string
     # @param value ? 值
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月18日 09:25:12
    """
    def setListVarByNameValue(self, name, value):
        if not name:
            return False
        if not value:
            return False
        emptyList = []
        className = self.__class__.__name__

        if className:
            gName = className + '_' + name
        else:
            gName = name

        originalVlaue = self.getVarByName(name)
        if originalVlaue:
            emptyList = originalVlaue
        emptyList.append(value)
        setattr(g, gName, emptyList)

    """
     # 重置值
     # @param self
     # @param name string
     # @param value ? 值
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月18日 10:57:37
    """

    def resetVarByName(self, name):
        if not name:
            return False

        className = self.__class__.__name__
        if className:
            gName = className + '_' + name
        else:
            gName = name

        setattr(g, gName, '')

    """
     # 重置值
     # @param self
     # @param name string
     # @param value ? 值
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月18日 10:57:37
    """

    def resetListVarByName(self, name):
        if not name:
            return False

        className = self.__class__.__name__
        if className:
            gName = className + '_' + name
        else:
            gName = name

        setattr(g, gName, [])

    """
     # 返回值
     # @param self
     # @param name string
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月18日 09:25:16
    """

    def getVarByName(self, name):
        if not name:
            return False

        className = self.__class__.__name__
        if className:
            gName = className + '_' + name
        else:
            gName = name

        if hasattr(g, gName):
            return getattr(g, gName)
        return False

    def getName(self, name):
        className = self.__class__.__name__
        if className:
            gName = className + '_' + name
        else:
            gName = name
        return gName

    pass

