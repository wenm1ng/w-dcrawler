# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time      :   2022/5/11 14:00
# @Author    :   WenMing
# @Desc      :   
# @Contact   :   736038880@qq.com
import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
from urllib.parse import urlparse
import Configs.mysql as mysqlConfig
class MysqlPool(object):

    def __init__(self):
        self.POOL = PooledDB(
            creator=pymysql,
            maxconnections=mysqlConfig.max_connections,  # 连接池的最大连接数
            maxcached=mysqlConfig.max_cached,
            maxshared=mysqlConfig.max_shared,
            blocking=mysqlConfig.blocking,
            setsession=mysqlConfig.set_session,
            host=mysqlConfig.host,
            port=mysqlConfig.port,
            user=mysqlConfig.user,
            password=mysqlConfig.password,
            database=mysqlConfig.database,
            charset='utf8',
        )
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
        return cls._instance

    def connect(self):
        conn = self.POOL.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        return conn, cursor

    def connect_close(self,conn, cursor):
        cursor.close()
        conn.close()

    def fetch_all(self,sql, args):
        conn, cursor = self.connect()
        if args is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, args)
        record_list = cursor.fetchall()
        return record_list

    def fetch_one(self,sql, args):
        conn, cursor = self.connect()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        return result

    def insert(self,sql, args):
        conn, cursor = self.connect()
        row = cursor.execute(sql, args)
        conn.commit()
        self.connect_close(conn, cursor)
        return row

    def getWhere(self, where):
        whereArr = []
        args = []

        if '=' in where.keys():
            for key in where['=']:
                # keyStr = str(where['='][key])
                whereArr.append(key + ' = %s')
                args.append(where['='][key])
        if 'in' in where.keys():
            for key in where['in']:
                keyStr = '('
                for item in where['in'][key]:
                    keyStr += item + ','
                keyStr = keyStr.strip(',') + ')'
                whereArr.append(key + ' in %s')
                args.append(keyStr)
        whereStr = ' and '.join(whereArr)
        return {'where': whereStr, 'args': args}

    def get(self, table, where, fields):
        conn, cursor = self.connect()
        result = self.getWhere(where)
        whereStr = result['where']
        args = result['args']
        sql = '''
        select {fields} from {table} where {whereStr}
        '''.format(table=table, fields=fields, whereStr=whereStr)
        cursor.execute(sql, args)
        record_list = cursor.fetchall()
        return record_list

    def first(self, table, where, fields='*'):
        conn, cursor = self.connect()
        result = self.getWhere(where)
        whereStr = result['where']
        args = result['args']
        sql = '''
                select {fields} from {table} where {whereStr} limit 1
                '''.format(table=table, fields=fields, whereStr=whereStr)
        cursor.execute(sql, args)
        record_info = cursor.fetchall()
        if record_info and record_info[0]:
            return record_info[0]
        else:
            return {}

    #
    #fields = ['id', 'app_id' ,'app_name']
# >>> data = [{'id': 6, 'app_id': '006', 'app_name': 'Solor'}, {'id': 7, 'app_id': '007', 'app_name': 'Symbian'}]
# >>> client.upsert_to_mysql(table='conn_pool_test', fields=fields, records=data)
    # 批量插入数据
    #
    def batch_insert(self, table, fields, items):
        # client.upsert_to_mysql(table='conn_pool_test', fields=fields, records=data)
        conn, cursor = self.connect()

        try:
            alias = 'new'
            fields_str = ','.join(fields)
            replace_str = ','.join(['%s' for _ in range(len(fields))])
            fields_update_str = ','.join(['{first}={alias}.{second}'.format(first=field, alias=alias, second=field) for field in fields])
            sql = '''
            insert ignore into {table} ( {fields} ) values ({replace_str}) as {alias}
            on duplicate key update {fields_update}
            '''.format(table=table, replace_str=replace_str, fields=fields_str, fields_update=fields_update_str, alias=alias)
            print(sql)

            records = []
            for item in items:
                row = tuple([item[field] for field in fields])
                records.append(row)
            cursor.executemany(sql, records)
            print(records)
            row = cursor.lastrowid
            conn.commit()
            return row
        except Exception as e:
            print('error file:' + e.__traceback__.tb_frame.f_globals["__file__"] + '_line:' + str(
                e.__traceback__.tb_lineno) + '_msg:' + str(e))  # 发生异常所在的文件
            conn.rollback()
            raise AssertionError(e)
