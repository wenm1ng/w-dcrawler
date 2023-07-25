# coding: utf-8
from flask_apscheduler import APScheduler
from App.service.proxyPool.setProxyPoolService import setProxyPoolService
from App.service.system.distributed.distributedPoolInfomationService import distributedPoolInfomationService
from flask import Flask

app = Flask(__name__)
'''
 # 定时任务控制器
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月7日 16:53:59
 # @version     0.1.0 版本号
'''


class indexCrontab(object):
    """
     # 设置
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2020年8月11日 14:51:25
    """

    def setAPSchedulerTask(self):
        scheduler = APScheduler()
        scheduler.add_job(func=self.refreshProxyInfomation, max_instances=10, id='checkProxy.refreshProxyInfomation', trigger='interval', seconds=180, replace_existing=True)
        # scheduler.add_job(func=self.refreshDistributedInfomation, max_instances=10, id='config.refreshDistributedInfomation', trigger='interval', seconds=5, replace_existing=True)
        scheduler.start()

    """
     # 刷新代理
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:56:22
    """

    def refreshProxyInfomation(self):
        ctx = app.app_context()
        ctx.push()
        setProxyPoolService().getProxyPoolsetPools()
        ctx.pop()
        # exit()

    """
     # 刷新分布式
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:56:22
    """

    def refreshDistributedInfomation(self):
        ctx = app.app_context()
        ctx.push()
        distributedPoolInfomationService().setDistributedPool()
        print("I'm a refreshDistributedInfomation!")
        ctx.pop()
