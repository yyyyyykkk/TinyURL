# -*- coding: utf-8 -*-

import logging
from tablestore import *
from tablestore.retry import WriteRetryPolicy
from hashids import Hashids
import json

table_name = 'TinyURLData'

client = OTSClient('table store endpoint', 'access key id', 
'secret key', 'instance id', logger_name = 'table_store.log',  
retry_policy = WriteRetryPolicy())

SALT = 'tinyurl'

def get_content(auto_id):
    primary_key = [('gid',1), ('uid',auto_id)]
    columns_to_get = ['content']
    try:
        # 调用get_row接口查询，最后一个参数值1表示只需要返回一个版本的值。
        _, return_row, next_token = client.get_row(table_name, primary_key, columns_to_get, None, 1)
        return json.dumps(return_row.attribute_columns[0][1])
    # 客户端异常，一般为参数错误或者网络异常。
    except OTSClientError as e:
        print "get row failed, http_status:%d, error_message:%s" % (e.get_http_status(), e.get_error_message())
    # 服务端异常，一般为参数错误或者流控错误。
    except OTSServiceError as e:
        print "get row failed, http_status:%d, error_code:%s, error_message:%s, request_id:%s" % (e.get_http_status(), e.get_error_code(), e.get_error_message(), e.get_request_id())

def handler(environ, start_response):
    context = environ['fc.context']
    request_uri = environ['fc.request_uri']
    for k, v in environ.items():
      if k.startswith('HTTP_'):
        # process custom request headers
        pass

    hash_str = request_uri.split('/')[-1]

    hashid = Hashids(salt=SALT)
    auto_id = hashid.decode(hash_str)[0]

    status = '200 OK'
    response_headers = [('Content-type', 'application/json')]
    start_response(status, response_headers)
    return get_content(auto_id)