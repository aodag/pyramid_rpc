# -*- coding:utf-8 -*-

import unittest
import sys

from pyramid import testing

class TestJSONRPCEndPoint(unittest.TestCase):
    def setUp(self):
        testing.cleanUp()
        from pyramid.threadlocal import get_current_registry
        self.registry = get_current_registry()

    def tearDown(self):
        testing.cleanUp()

    def _getTargetClass(self):
        from pyramid_rpc.jsonrpc1 import jsonrpc_endpoint
        return jsonrpc_endpoint

    def _makeOne(self, *arg, **kw):
        return self._getTargetClass()

    def _registerRouteRequest(self, name):
        from pyramid.interfaces import IRouteRequest
        from pyramid.request import route_request_iface
        iface = route_request_iface(name)
        self.registry.registerUtility(iface, IRouteRequest, name=name)
        return iface

    def _registerView(self, app, name, classifier, req_iface, ctx_iface):
        from pyramid.interfaces import IView
        self.registry.registerAdapter(
            app, (classifier, req_iface, ctx_iface), IView, name)
    
    def _makeDummyRequest(self):
        from pyramid.testing import DummyRequest
        return DummyRequest()
    
    def test_jsonrpc_endpoint(self):
        from pyramid.interfaces import IViewClassifier
        view = DummyView({'name': 'Smith'})
        rpc2_iface = self._registerRouteRequest('RPC2')
        self._registerView(view, 'echo', IViewClassifier, rpc2_iface, None)
        
        jsonrpc_endpoint = self._makeOne()
        request = self._makeDummyRequest()
        request.body = DummyJSONBody1
        request.matched_route = DummyRoute('RPC2')
        response = jsonrpc_endpoint(request)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.body, '{"errors": null, "result": {"name": "Smith"}, "id": "test-echo"}')
    
    def test_jsonrpc_endpoint_notify(self):
        from pyramid.interfaces import IViewClassifier
        view = DummyView({'name': 'Smith'})
        rpc2_iface = self._registerRouteRequest('RPC2')
        self._registerView(view, 'echo', IViewClassifier, rpc2_iface, None)
        
        jsonrpc_endpoint = self._makeOne()
        request = self._makeDummyRequest()
        request.body = DummyJSONBody2
        request.matched_route = DummyRoute('RPC2')
        response = jsonrpc_endpoint(request)
        self.assertEqual(response.body, '')

    def test_jsonrpc_endpoint_not_found(self):
        from pyramid.interfaces import IViewClassifier
        from pyramid.exceptions import NotFound
        jsonrpc_endpoint = self._makeOne()
        request = self._makeDummyRequest()
        request.body = DummyJSONBody1
        request.matched_route = DummyRoute('RPC2')
        response = jsonrpc_endpoint(request)
        self.assertEqual(response.message, "No method of that name was found.")


DummyJSONBody1 = """{"method": "echo", "params": [13], "id": "test-echo"}"""
DummyJSONBody2 = """{"method": "echo", "params": [13]}"""

class DummyRoute:
    def __init__(self, route_name):
        self.name = route_name

class DummyView:
    def __init__(self, response, raise_exception=None):
        self.response = response
        self.raise_exception = raise_exception

    def __call__(self, context, request):
        self.context = context
        self.request = request
        return self.response

class DummyVenusianInfo(object):
    scope = 'notaclass'
    module = sys.modules['pyramid_rpc.tests']
    codeinfo = None

class DummyVenusian(object):
    def __init__(self, info=None):
        if info is None:
            info = DummyVenusianInfo()
        self.info = info
        self.attachments = []

    def attach(self, wrapped, callback, category=None):
        self.attachments.append((wrapped, callback, category))
        return self.info

class DummyConfig(object):
    def __init__(self):
        self.settings = []

    def add_view(self, **kw):
        self.settings.append(kw)

class DummyVenusianContext(object):
    def __init__(self):
        self.config = DummyConfig()
        
def call_venusian(venusian):
    context = DummyVenusianContext()
    for wrapped, callback, category in venusian.attachments:
        callback(context, None, None)
    return context.config.settings

class TestJSONRPCParse(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from pyramid_rpc.jsonrpc1 import jsonrpc_parse
        return jsonrpc_parse(*args, **kwargs)

    def test_it(self):
        data = '{"method": "method_name", "params":[1, 2], "id":"a"}'
        method, params, res_id = self._callFUT(data)

