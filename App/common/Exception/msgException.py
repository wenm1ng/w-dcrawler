# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time      :   2022/5/12 17:50
# @Author    :   WenMing
# @Desc      :   
# @Contact   :   736038880@qq.com
class msgException(Exception):
    # "this is user's Exception for check the length of name "
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        print(self.msg)
