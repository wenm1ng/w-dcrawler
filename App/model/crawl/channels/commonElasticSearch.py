# coding: utf-8
from random import random, randint
import elasticsearch
from App.common.model.baseElasticsearch import baseElasticsearch
from Configs import defaultApp
import json

'''
 # 设置代理池
 # @author      WenMing    736038880@qq.com
 # @createTime  2020年12月31日 17:37:03
 # @version     0.1.0 版本号
'''


class commonElasticSearch(object):
    """
     # 获取数据
     # @param self
     # @param index
     # @param id
     # @param doc_type
     # @return string
     # @author     WenMing    736038880@qq.com
     # @createTime 2021年4月1日 17:10:11
    """

    def getSourceByIndexKey(self, index, id, doc_type="_doc", elasticsearchType=0):
        result = False
        try:
            data = self.getConnectElasticsearch(elasticsearchType).get(index=index, doc_type=doc_type, id=id)
            print("es_data:", json.dumps(data))
            if data:
                if '_source' in data.keys():
                    result = data['_source']
        except exceptions.NotFoundError:
            print("找不到当前数据!")
            pass

        return result

    def getByEsSearch(self, index, KQLdata, elasticsearchType=0):
        datalist = None
        try:
            datalist = self.getConnectElasticsearch(elasticsearchType).search(index=index, body=KQLdata)
        except exceptions.NotFoundError:
            print("找不到当前数据!")
            pass
        return datalist

    def getByEsSearch2(self, index, scroll, size, body, elasticsearchType=0):
        datalist = self.getConnectElasticsearch(elasticsearchType).search(index=index,
                                                                          scroll=scroll, size=size, body=body)
        return datalist

    def getByEsscroll(self, scroll_id, scroll, elasticsearchType=0):
        datalist = self.getConnectElasticsearch(elasticsearchType).scroll(scroll_id=scroll_id,scroll=scroll)
        return datalist

    def clear_scroll(self, scroll_id,elasticsearchType=0):
        self.getConnectElasticsearch(elasticsearchType).clear_scroll(scroll_id=scroll_id)
        return


    def getByEsCount(self, index, KQLdata, elasticsearchType=0):
        datalist = self.getConnectElasticsearch(elasticsearchType).count(index=index, body=KQLdata)
        return datalist

    def insertDataByIndexKey(self, index, id, data, doc_type="_doc", elasticsearchType=0):
        result = False
        q = self.getConnectElasticsearch(elasticsearchType).index(index=index, doc_type=doc_type, id=id, body=data)
        print('es_code:', q)
        result = True
        return result


    def updataDataByIndexKey(self, index, id, data, elasticsearchType=0):
        result = False
        esdata = {"doc": data}
        q = self.getConnectElasticsearch(elasticsearchType).update(index=index, id=id, body=esdata)
        print('es_code:', q)
        result = True
        return result

    def getConnectElasticsearch(self, elasticsearchType=0):
        return baseElasticsearch.connectElasticsearch(self, elasticsearchType)
