# coding: utf-8

from Configs import defaultApp
if defaultApp.isGevent:
    import gevent
    from gevent import monkey
    monkey.patch_all()
from App import app
# from App.crontab.indexCrontab import indexCrontab
from App.service.system.taskService import taskService




if __name__ == '__main__':
    if defaultApp.isTask:
        taskService().execMain()
        # indexCrontab().setAPSchedulerTask()
    app.run(
        host=defaultApp.host,
        port=defaultApp.port,
        debug=defaultApp.debug,
        # processes=defaultApp.processesNum,
        threaded=defaultApp.threadedStatus,
    )
