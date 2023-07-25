# coding: utf-8

import requests, json,os,gzip,base64
import random
from Configs import defaultApp
import platform


'''
 # ua获取类
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年3月31日 16:36:48
 # @version     0.1.0 版本号
'''


class osSystemCrawl(object):

    """
     # 异步启动脚本采集
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年3月31日 16:37:03
    """

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

    """
     # gzip 压缩 base64
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年6月8日 11:20:28
    """
    def compressGzipBase64(self,content):
        if not content:
            return
        if type(content) != 'str':
            content = str(content).encode("utf-8")

        bytesGzipCompress = gzip.compress(content)
        base64Data = base64.b64encode(bytesGzipCompress)
        result = str(base64Data.decode())
        return result

    """
     # gzip 解压 base64
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年6月8日 11:20:28
    """
    def decompressGzipBase64(self,content):
        if not content:
            return
        base64Data = base64.b64decode(content)
        bytesGzipDecompress = gzip.decompress(base64Data)
        result = bytesGzipDecompress.decode()
        return result


