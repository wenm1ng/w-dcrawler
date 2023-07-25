# coding: utf-8
import os
import elasticsearch
from Configs import elasticsearch as conElasticsearch


class baseElasticsearch(object):
    def connectElasticsearch(self, elasticsearchType=0):
        try:
            connectInfo = conElasticsearch.elasticsearchConfigList[elasticsearchType]
            # print(connectInfo)
            host = connectInfo['host']
            port = connectInfo['port']
            user = connectInfo['user']
            password = connectInfo['password']
            timeout = connectInfo['timeout']

            return Elasticsearch(
                [
                    host
                ],
                port=port,
                http_auth=(user, password),
                timeout=timeout
            )
        except Exception as e:
            print(1111)

        return False
