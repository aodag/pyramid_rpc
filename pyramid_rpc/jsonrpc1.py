# -*- coding:utf-8 -*-

import sys

try:
    import json
except ImportError:
    import simplejson as json
    sys.modules['json'] = json

from pyramid_rpc.api import view_lookup
from pyramid.response import Response
from pyramid.exceptions import NotFound

def jsonrpc_parse(data):
    jsondata = json.loads(data)
    method = jsondata['method']
    params = jsondata['params']
    res_id = jsondata.get('id')
    return method, params, res_id

def jsonrpc_marshal(data, res_id, errors=None):
    return json.dumps({'result': data, 'errors': errors, 'id': res_id})

def jsonrpc_endpoint(request):
    """ A base view to be used with add_route to setup an JSON-RPC dispatch 
    endpoint
    """
    method, params, res_id = jsonrpc_parse(request.body)
    request.rpc_args = params

    view_callable = view_lookup(request, method)
    if not view_callable:
        return NotFound("No method of that name was found.")

    data = view_callable(request.context, request)
    if res_id is not None:
        jsondata = jsonrpc_marshal(data, res_id)
        response = Response(jsondata)
        response.content_type = 'application/json'
        response.content_length = len(jsondata)
    else:
        response = Response()
        
    return response

