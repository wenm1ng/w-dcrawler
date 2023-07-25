#!/usr/bin/python
# -*- coding:utf-8 -*-
from App import app
from Configs import defaultApp
import sys, os
import importlib
from pathlib import Path

if __name__ == '__main__':
    rangeLen = 1
    if len(sys.argv) < 1:
        print('=' * 50)
        print('0:command.py')
        print('1:渠道')
        print('2:站点')
        print('3:方法')
        print('4:需要执行多少个脚本')
        print('=' * 50)

    execPath = defaultApp.rootDir + os.sep + 'App' + os.sep + 'script' + os.sep + sys.argv[1] + os.sep + sys.argv[
        2] + os.sep + sys.argv[3] + '.py'

    if len(sys.argv) == 5:
        rangeLen = int(sys.argv[4])
        for i in range(rangeLen):
            indexExecPath = defaultApp.rootDir + os.sep + 'App' + os.sep + 'script' + os.sep + sys.argv[1] + os.sep + \
                            sys.argv[2] + os.sep + sys.argv[3] + str(i) + '.py'
            my_file = Path(indexExecPath)
            if my_file.is_file():
                continue

            execPathOpen = open(execPath, 'r', encoding='utf-8')
            print(execPathOpen)
            with open(indexExecPath, 'w', encoding='utf-8') as f:
                f.write(execPathOpen.read())
            execPathOpen.close()

            os.system("nohup  python " + indexExecPath + " &")

    if len(sys.argv) == 6:
        os.system("python %s" % execPath)