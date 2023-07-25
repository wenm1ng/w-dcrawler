# coding: utf-8
from flask import Flask
import logging, os, time, json
from App import app
from Configs import defaultApp
from App.model.crawl.channels.commonRedis import commonRedis
from pathlib import Path
import platform

'''
 # 设置分布式副本情况
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月7日 16:24:18
 # @version     0.1.0 版本号
'''


class taskService(object):
    """
     # 执行任务
     # @param self
     # @param fileName 文件名称
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年6月8日 16:42:11
    """

    def execMain(self):
        # 初始化,为空，就推进
        commonRedisClass = commonRedis()
        runTaskList = commonRedisClass.getListDataByKey('runtask', redisType=1)
        print(runTaskList)
        if not runTaskList:
            runTaskLogList = defaultApp.runTaskLog
            if runTaskLogList:
                for runTaskLogListValue in runTaskLogList:
                    commonRedisClass.redispush(flag=0, redisKeyName='runtask', data=runTaskLogListValue, redisType=1)

        # 获取任务
        task = commonRedisClass.getRpopListDataByKey(redisKeyName='runtask', redisType=1)
        # 执行任务
        if not task:
            return

        taskList = task.split(',')
        print(task)
        print(taskList[0])
        if taskList[0] == '1':
            path = defaultApp.rootDir + os.sep + 'App' + os.sep + 'script' + os.sep + taskList[1] + os.sep + taskList[2]
            for key, value in enumerate(taskList):
                if key <= 2:
                    continue
                taskValue = value.split(':')
                print(taskValue)
                for i in range(int(taskValue[1])):
                    execPath = path + os.sep + taskValue[0] + '.py'
                    indexExecPath = path + os.sep + taskValue[0] + str(i) + '.py'
                    my_file = Path(indexExecPath)
                    if my_file.is_file():
                        self.execCommand(indexExecPath)
                        continue
                    execPathOpen = open(execPath, 'r', encoding='utf-8')
                    print(execPathOpen)
                    with open(indexExecPath, 'w', encoding='utf-8') as f:
                        f.write(execPathOpen.read())
                    execPathOpen.close()

                    self.execCommand(indexExecPath)

        if taskList[0] == '2':
            path = defaultApp.rootDir + os.sep + 'App' + os.sep + 'script' + os.sep + taskList[1]
            dirs = os.listdir(path)
            # 输出所有文件和文件夹
            for file in dirs:
                sitePath = path + os.sep + file
                print(sitePath)
                for key, value in enumerate(taskList):
                    if key <= 1:
                        continue
                    taskValue = value.split(':')
                    print(taskValue)
                    for i in range(int(taskValue[1])):
                        execPath = sitePath + os.sep + taskValue[0] + '.py'
                        indexExecPath = sitePath + os.sep + taskValue[0] + str(i) + '.py'
                        my_file = Path(indexExecPath)
                        if my_file.is_file():
                            self.execCommand(indexExecPath)
                            continue
                        execPathOpen = open(execPath, 'r', encoding='utf-8')
                        print(execPathOpen)
                        with open(indexExecPath, 'w', encoding='utf-8') as f:
                            f.write(execPathOpen.read())
                        execPathOpen.close()



    """
     # 执行任务
     # @param self
     # @param fileName 文件名称
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年6月8日 16:42:11
    """

    def execCommand(self,indexExecPath):
        if not indexExecPath:
            return
        if platform.system() == 'Windows':
            command = "start python " + indexExecPath + " "
        else:
            command = "nohup  python " + indexExecPath + " &"
        os.system(command)
        print(command)