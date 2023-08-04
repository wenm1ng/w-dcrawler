"""
 # 判断值类型
 # @param self
 # @return string
 # @author     WenMing    736038880@qq.com
 # @createTime 2021年1月8日 15:22:56
"""

import random
import urllib

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


def is_contain_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

"""
 # 替换url参数的值
"""
def replaceUrlParam(param_old, dict_new):
    dict_old = dict(urllib.parse.parse_qsl(param_old)) #将①的所有key值拿出来
    for (key, value) in dict_old.items():#替换掉key值
        if not key in dict_new:
            continue
        temp = dict_new[key]
        dict_old[key] = temp
    param_new = urllib.parse.unquote(urllib.parse.urlencode(dict_old))#组合成新的url
    return param_new

def getUrlParam(param):
    return dict(urllib.parse.parse_qsl(param))