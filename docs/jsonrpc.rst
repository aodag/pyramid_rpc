.. _jsonrpc:

============
JSON-RPC
============

Exposing JSON-RPC Methods
===========================

Supporting JSON-RPC is similar to XML-RPC support.
Thus, the same way to expose JSON-RPC methods can be used.

Example:

.. code-block:: python
    :linenos:

    @xmlrpc_view()
    def say_hello(request):
        return 'Hello, %s' % request.xmlrpc_args['name']

.. code-block:: python
   :linenos:

   config.scan()
   config.add_route('RPC2', '/api/jsonrpc', view='pyramid_rpc.jsonrpc_endpoint')

Call Example
=================

Then call the function via an urllib2 library.

.. code-block:: python
    :linenos:

    >>> from urllib2 import urlopen
    >>> res = urlopen('http://localhost:6543/jsonrpc', '{"method": "say_hello", "params": ["Chris"], "id": "hello"')
    >>> res.read()
    '{"errors": null, "result": "Hello, Chris", "id": "hello"}'


.. _jsonrpc_api

API
====

Public
--------

.. automodule:: pyramid_rpc.jsonrpc

  .. autofunction:: jsonrpc_endpoint

