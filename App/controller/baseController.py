# coding: utf-8
from flask import jsonify
import json
from flask import request
from App.service.system.classContextService import classContextService

'''
 # 基类控制器
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class baseController(object):

    def __init__(self):
        self.setJsonParams()

    """
     # json封装
     # @val  array
    """
    apiResult = {
        'code': 400,
        'msg': '',
        'data': [],
    }

    """
     # 设置json接受消息
     # @param self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年12月31日 17:41:34
    """

    def setJsonParams(self):
        try:
            if request.get_data(as_text=True):
                classContextService().setVarByNameValue(name=self.__class__.__name__ + '_jsonParams', value=json.loads(request.get_data(as_text=True)))
            if request.method == 'GET':
                if request.args:
                    classContextService().setVarByNameValue(name=self.__class__.__name__ + '_getParams', value=request.args)
        except Exception as e:
            classContextService().resetVarByName(name=self.__class__.__name__ + '_jsonParams')
            classContextService().resetVarByName(name=self.__class__.__name__ + '_getParams')

    """
     # 设置json返回消息
     # @param self
     # @param string msg
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年12月31日 17:41:34
    """

    def setApiResultMsg(self, msg):
        self.apiResult['msg'] = msg

    """
     # 设置json返回数据集
     # @param self
     # @param string data
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年12月31日 17:41:34
    """

    def setApiResultData(self, data):
        self.apiResult['data'] = data

    """
     # 设置json成功返回码
     # @param  self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年12月31日 17:41:34
    """

    def setSuccessCode(self):
        self.apiResult['code'] = 200

    """
     # 设置json失败返回码
     # @param  self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年12月31日 17:41:34
    """

    def setFailCode(self):
        self.apiResult['code'] = 400

    """
     # 输出json
     # @param  self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年12月31日 17:41:34
    """

    def outputJson(self,apiResult=None):
        if apiResult:
            return jsonify(apiResult)
        return jsonify(self.apiResult)
