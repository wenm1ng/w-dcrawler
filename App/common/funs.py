"""
 # 判断值类型
 # @param self
 # @return string
 # @author     WenMing    736038880@qq.com
 # @createTime 2021年1月8日 15:22:56
"""

import random

def checkValueType(value):
    type = None
    if isinstance(value, int):
        type = "int"
    elif isinstance(value, str):
        type = "str"
    elif isinstance(value, float):
        type = "float"
    elif isinstance(value, list):
        type = "list"
    elif isinstance(value, tuple):
        type = "tuple"
    elif isinstance(value, dict):
        type = "dict"
    elif isinstance(value, set):
        type = "set"

    return type


"""
 # 追加词典
 # @param dictData  词典数据
 # @param mainKey   主键
 # @param key       键
 # @param value     值
 # @return string
 # @author     WenMing    736038880@qq.com
 # @createTime 2021年1月20日 14:57:24
"""


def appendDict(dictData, mainKey, key, value):
    if mainKey in dictData:
        dictData[mainKey].update({key: value})
    else:
        dictData.update({mainKey: {key: value}})
    return dictData


"""
 # 获取最右边第一个值，通过符号
 # @param dictData  词典数据
 # @param mainKey   主键
 # @param key       键
 # @param value     值
 # @return string
 # @author     WenMing    736038880@qq.com
 # @createTime 2021年6月10日 15:24:25
"""


def getFirstRightValueByMark(matchString, mark):
    if not matchString or not mark:
        return ''
    pathIndex = matchString.rfind(mark)
    if not pathIndex:
        return ''
    return matchString[pathIndex + 1:]

# 返回随机字符串
def random_string_generator(str_size):
    return ''.join(random.choice('qwertyuiopasdfghjklzxcvbnm1234567890') for x in range(str_size))