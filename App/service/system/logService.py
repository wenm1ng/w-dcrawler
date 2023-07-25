# coding: utf-8
from flask import Flask
import logging, os, time, json
from App import app
from Configs import defaultApp

'''
 # 设置分布式副本情况
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月7日 16:24:18
 # @version     0.1.0 版本号
'''


class logService(object):
    """
    # 文件夹
    # @var string
    """
    logDirName = 'Logs'

    """
    # 日志前缀
    # @var string
    """
    logFilePrefixName = 'log-'

    """
    # 日志尾缀
    # @var string
    """
    logFileTailName = '.log'

    """
     # 设置日志，默认格式
     # @param self
     # @param fileName 文件名称
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月11日 14:54:38
    """

    def setLogDefaultConfigs(self, fileName=None):
        if not fileName:
            logFileName = self.logFilePrefixName + time.strftime('%Y-%m-%d', time.localtime(time.time())) + self.logFileTailName
        else:
            logFileName = self.logFilePrefixName + fileName + self.logFileTailName

        log_file_folder = defaultApp.rootDir + os.sep + self.logDirName
        self.makeDir(make_dir_path=log_file_folder)
        log_file_str = log_file_folder + os.sep + logFileName
        handler = logging.FileHandler(log_file_str, encoding='UTF-8')
        logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
        handler.setFormatter(logging_format)

        app.logger.addHandler(handler)

    """
     # 日志
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月11日 14:55:03
    """

    def log(self, msg, logLevel=None, fileName=None):
        self.setLogDefaultConfigs(self, fileName=fileName)
        app.logger.log(msg=json.loads(msg), level=logLevel)

    """
     # info
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月11日 14:55:03
    """

    def info(self, msg, fileName=None):
        self.setLogDefaultConfigs(fileName=fileName)
        app.logger.info(msg=msg)

    """
     # debug
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月11日 14:55:03
    """

    def debug(self, msg, fileName=None):
        self.setLogDefaultConfigs(self, fileName=fileName)
        app.logger.debug(msg=msg)

    """
     # debug
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月11日 14:55:03
    """

    def writeLog(self, msg, fileName=None):
        logFileName = self.logFilePrefixName + fileName + self.logFileTailName
        log_file_folder = defaultApp.rootDir + os.sep + self.logDirName
        log_file_str = log_file_folder + os.sep + logFileName
        with open(log_file_str, 'w') as f:
            f.write(msg)

    def getWriteLogFileName(self, fileName=None):
        logFileName = self.logFilePrefixName + fileName + self.logFileTailName
        log_file_folder = defaultApp.rootDir + os.sep + self.logDirName
        return log_file_folder + os.sep + logFileName

    """
     # 新建文件
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月11日 14:55:03
    """

    def makeDir(self, make_dir_path):
        path = make_dir_path.strip()
        if not os.path.exists(path):
            os.makedirs(path)

    pass
