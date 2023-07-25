# coding: utf-8
from App.common.webRequest import WebRequest
from App.model.system.distributed.redis.distributedPoolInfomationRedis import distributedPoolInfomationRedis
from Configs import defaultApp

'''
 # 设置分布式副本情况
 # @author      WenMing    736038880@qq.com
 # @createTime  2021年1月7日 16:24:18
 # @version     0.1.0 版本号
'''


class distributedPoolInfomationService(object):
    """
    # 获取当前结果词典
    # @var dict
    """
    dpResult = {}

    """
    # 当前项目
    # @var string
    """
    currentProject = ''

    """
    # 当前项目分支
    # @var string
    """
    currentProjectBranch = ''

    """
    # 当前项目分支ID
    # @var string
    """
    currentProjectBranchIdItem = ''

    """
     # 设置分布式池
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def setDistributedPool(self):
        result = False
        url = defaultApp.rancherUrl
        if not url:
            return result
        rancherProjects = defaultApp.rancherProjects
        if not rancherProjects:
            return result
        appendHeader = {
            'Accept': 'application/json',
            'Authorization': 'Basic ' + defaultApp.rancherProjectsBasicAuth
        }
        if not url:
            return ''
        if not rancherProjects:
            return ''
        for rancherProjectsKey in rancherProjects:
            if not rancherProjectsKey:
                continue
            if not rancherProjects[rancherProjectsKey]:
                continue
            self.currentProject = rancherProjectsKey
            # self.updateDefaultCurrentProject()
            for rancherProjectsKeyKey in rancherProjects[rancherProjectsKey]:
                if not rancherProjectsKeyKey:
                    continue
                if not rancherProjects[rancherProjectsKey][rancherProjectsKeyKey]:
                    continue
                self.currentProjectBranch = rancherProjectsKeyKey
                # self.updateDefaultCurrentProjectBranch()
                resp = WebRequest().get(url + '/v3/project/' + rancherProjects[rancherProjectsKey][rancherProjectsKeyKey] + '/pods/', header=appendHeader, timeout=10)
                self.assembleData(primevalData=resp.json())
        # print(self.dpResult)
        self.saveDpResult()

    # def updateDefaultCurrentProject(self):
    #     self.dpResult.update({
    #         self.currentProject: {
    #         }
    #     })
    #
    # def updateDefaultCurrentProjectBranch(self):
    #     self.dpResult[self.currentProject].update({
    #         self.currentProjectBranch: {
    #         }
    #     })

    """
     # 设置默认值
     # @param self
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def updateDefaultCurrentProjectBranchIdItem(self):
        self.dpResult.update({
            self.currentProjectBranchIdItem: {
                'podName': '',
                'itemName': '',
                'podSpaceId': '',
                'podId': '',
                'podIp': '',
                'podstartTime': 0,
                'projectId': '',
                'state': '',
                'uuid': '',
            }
        })

    """
     # 组装格式
     # @param self
     # @param primevalData 当前json
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def assembleData(self, primevalData):
        result = False
        if not primevalData:
            return result
        if 'data' not in primevalData.keys():
            return result
        if not primevalData['data']:
            return result

        for primevalDataKey in primevalData['data']:
            currentPrimevalData = primevalDataKey
            if 'id' not in currentPrimevalData.keys():
                continue

            self.currentProjectBranchIdItem = currentPrimevalData['id']
            self.updateDefaultCurrentProjectBranchIdItem()

            if 'labels' in currentPrimevalData.keys():
                if 'app' in currentPrimevalData['labels'].keys():
                    self.dpResult[self.currentProjectBranchIdItem]['itemName'] = currentPrimevalData['labels']['app']
            if 'name' in currentPrimevalData.keys():
                self.dpResult[self.currentProjectBranchIdItem]['podName'] = currentPrimevalData['name']
            if 'namespaceId' in currentPrimevalData.keys():
                self.dpResult[self.currentProjectBranchIdItem]['podSpaceId'] = currentPrimevalData['namespaceId']
            if 'nodeId' in currentPrimevalData.keys():
                self.dpResult[self.currentProjectBranchIdItem]['podId'] = currentPrimevalData['nodeId']
            if 'status' in currentPrimevalData.keys():
                if 'podIp' in currentPrimevalData['status'].keys():
                    self.dpResult[self.currentProjectBranchIdItem]['podIp'] = currentPrimevalData['status']['podIp']
                if 'startTimeTS' in currentPrimevalData['status'].keys():
                    self.dpResult[self.currentProjectBranchIdItem]['podstartTime'] = currentPrimevalData['status']['startTimeTS']
            if 'projectId' in currentPrimevalData.keys():
                self.dpResult[self.currentProjectBranchIdItem]['projectId'] = currentPrimevalData['projectId']
            if 'state' in currentPrimevalData.keys():
                self.dpResult[self.currentProjectBranchIdItem]['state'] = currentPrimevalData['state']
            if 'uuid' in currentPrimevalData.keys():
                self.dpResult[self.currentProjectBranchIdItem]['uuid'] = currentPrimevalData['uuid']

    """
     # 存储格式
     # @param self
     # @return void
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年1月7日 16:26:06
    """

    def saveDpResult(self):
        result = False
        if not self.dpResult:
            return result

        for itemIdKey in self.dpResult:
            if self.dpResult[itemIdKey]:
                distributedPoolInfomationRedis().addListingProductHashDistributedPool(itemIdKey, self.dpResult[itemIdKey])

            # for branchKey in self.dpResult[projectKey]:
            #     if projectKey not in result.keys():
            #         result[branchKey] = {}
            #     for itemId in self.dpResult[projectKey][branchKey]:
            #         if branchKey not in result[projectKey].keys():
            #             result[branchKey][branchKey] = {}
            #         for itemValue in self.dpResult[projectKey][branchKey][itemId]:
            #             if itemValue['itemName'] in result[projectKey][branchKey].keys():
            #                 result[projectKey][branchKey][itemValue['itemName']] = itemValue
            #                 distributedPoolInfomationRedis().addProductHashDistributedPool(projectKey+branchKey,
            #                                                                            itemId, json.dumps(self.dpResult[projectKey][branchKey][itemId]))

    pass
