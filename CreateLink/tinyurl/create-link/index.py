# -*- coding: utf-8 -*-

import logging

from tablestore import *
from tablestore.retry import WriteRetryPolicy
from hashids import Hashids

table_name = 'TinyURLData'

client = OTSClient('table store endpoint', 'access key id', 
'secret key', 'instance id', logger_name = 'table_store.log',  
retry_policy = WriteRetryPolicy())

def create_table():
    # 创建表，表中包括两个主键：gid，INTEGER类型；uid，INTEGER类型，为自增列。
    schema_of_primary_key = [('gid', 'INTEGER'), ('uid', 'INTEGER', PK_AUTO_INCR)]
    defined_columns = [('content', 'STRING')]
    table_meta = TableMeta(table_name, schema_of_primary_key, defined_columns)
    table_options = TableOptions()
    reserved_throughput = ReservedThroughput(CapacityUnit(0, 0))
    client.create_table(table_meta, table_options, reserved_throughput)
    print ('Table has been created.')

def put_row(content):
    # 写入主键：gid为1，uid为自增列。uid列必须设置，否则报错。
    primary_key = [('gid',1), ('uid', PK_AUTO_INCR)]
    attribute_columns = [('content',content)]
    row = Row(primary_key, attribute_columns)

    consumed, return_row = client.put_row(table_name, row, return_type = ReturnType.RT_PK)
    return return_row.primary_key[1]

def update_row(hashstr, auto_id):
    # 主键的第一列是uid，值是整数1，第二列是gid，值是整数101。
    primary_key = [('gid',1), ('uid',auto_id)]

    update_of_attribute_columns = {
        'PUT' : [('hash',hashstr)],
    }
    row = Row(primary_key, update_of_attribute_columns)

    try:
        consumed, return_row = client.update_row(table_name, row, None, None)
    # 客户端异常，一般为参数错误或者网络异常。
    except OTSClientError as e:
        print "update row failed, http_status:%d, error_message:%s" % (e.get_http_status(), e.get_error_message())
    # 服务端异常，一般为参数错误或者流控错误。
    except OTSServiceError as e:
        print "update row failed, http_status:%d, error_code:%s, error_message:%s, request_id:%s" % (e.get_http_status(), e.get_error_code(), e.get_error_message(), e.get_request_id())

BASE_LINK = 'base link'
SALT = 'tinyurl'
def handler(environ, start_response):
    # create_table()

    context = environ['fc.context']
    request_uri = environ['fc.request_uri']

    for k, v in environ.items():
      if k.startswith('HTTP_'):
        # process custom request headers
        pass
    # do something here
    status = '200 OK'

    # get request_body    
    try:        
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))    
    except (ValueError):        
        request_body_size = 0   
    content = environ['wsgi.input'].read(request_body_size)

    _, auto_id = put_row(content)
    hashid = Hashids(salt=SALT)
    hash_str = hashid.encode(auto_id)

    update_row(hash_str, auto_id)

    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [BASE_LINK + hash_str]