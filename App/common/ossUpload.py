# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time      :   2022/5/11 11:33
# @Author    :   WenMing
# @Desc      :   
# @Contact   :   736038880@qq.com
import requests, json,os,gzip,base64
import random
from Configs import defaultApp
import platform
from qiniu import Auth
from qiniu import BucketManager
from App.common.funs import random_string_generator
'''
 # oss上传类
 # @author      wenming
 # @createTime  2022年5月11日 16:36:48
 # @version     0.1.0 版本号
'''


class ossUpload(object):
    __attrs__ = [
        'access_key', 'secret_key', 'bucket_name'
    ]

    def __init__(self):
        self.access_key = 'ggHrt3Fu7CMfTO8ICLKds99vBe7X40LTmrdVqvba'
        self.secret_key = 'CUtVdxc3EcGCj-2aYstVvyRbUlHvSmWRjB6ZHt9W'
        self.bucket_name = 'wm-wow'
        self.dir = 'wow/wa/image/'
        self.url = 'http://rbp8nkfkd.hn-bkt.clouddn.com'
    """
     # 异步启动脚本采集
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年3月31日 16:37:03
    """
    def uploadImageQiNiu(self, url):
        q = Auth(self.access_key, self.secret_key)
        bucket = BucketManager(q)
        key = self.dir+random_string_generator(10)+'.jpg'
        ret, info = bucket.fetch(url, self.bucket_name, key)
        assert ret['key'] == key
        return self.url+'/'+key

    def asynchUrlExecTask(self,jsonParams):
        if not jsonParams:
            return
        execPath = defaultApp.rootDir + os.sep + 'App' + os.sep + 'service' + os.sep + 'crawl' + os.sep +  'relayService.py'

        if platform.system() == 'Windows':
            command = "python " + execPath + " %s" % str(jsonParams)
        else:
            command = "nohup  python -u " + execPath + " %s" % str(jsonParams) + " &"
        print(command)
        os.system(command)