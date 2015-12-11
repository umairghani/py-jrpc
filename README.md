# Python Json RPC Server & Client
* Author: Umair Ghani

py-jrpc is a remote procedure call protocol encoded in JSON. It is a very simple protocol (and very similar to XML-RPC).

## Description:
### Server
LightWeight HTTP/HTTPS server with a REST API.

### Client
Help you connect to the Server and invoke functions on the server side.

## Dependencies:
* python2 (not tested on python3)
* python-crypto
* python-psutil (optional)

## Installation

```
pip install py-jrpc
easy_install py-jrpc

```

## Documentation
### Server
For able to support your own functions/modules, you need to register those methods with the server.
You would define your method and then register your methods with the class.

For example:

```

from jrpc import SimpleTCPServer as Server

def ping():
  return "pong"

if __name__ == "__main__":
  HOST, PORT = "localhost", 9999
  server = Server((HOST, PORT))
  server.register_function( ping )

  # To make it https
  server.socket = ssl.wrap_socket(server.socket, keyfile='key.pem', certfile='cacert.pem', server_side=True)
  server.register_function( ping )
  server.serve_forever()

```

In this example we defined "ping" method and then register that method to the class, so that it would be available for RPC.

You can also write your own multi threaded server by importing all the required classes.

```

from jrpc import SimpleTCPServer
from SocketServer import ThreadingMixIn

class Server(ThreadingMixIn,SimpleTCPServer):
  def __init__(self, bindaddr):
    SimpleTCPServer.__init__(self, bindaddr)
    self.register_function( ping )
    self.register_function( blah )

def ping():
  return "pong"

def blah(a):
  return a

if __name__ == "__main__":
  HOST, PORT = "localhost", 9999
  server = Server((HOST, PORT))

  # To make it https
  server.socket = ssl.wrap_socket(server.socket, keyfile='key.pem', certfile='cacert.pem', server_side=True)
  server.serve_forever()

```

### Client
The Server provides a REST API. You can write your own client in any language, you can even use curl commands to GET or POST:

#### Using cURL

```
$ curl --insecure https://myserver.com:9999/ping | python -mjson.tool
{
    "ping": "pong"
}

```

For POST, it requires a json object where the primary key would be name of the method.
For example:

```

$ curl --insecure -X POST https://myserver.com:9999 -d '{"ping":""}' | python -mjson.tool
{
    "ping": "pong"
}

```

To List all the methods, you can list_methods function, and that would return an array of all methods

```

$ curl --insecure https://myserver.com:9999/list_methods

```

For methods help, you can call method_help function:
(this information comes from pydoc)

```

$ curl --insecure -X POST https://myserver.com:9999 -d '{"method_help": "ping"}' | python -mjson.tool
{
    "method_help": ":return: response to ping"
}

```

#### SimpleTCPClient
The package comes with the SimpleTCPClient module can you can import and use that for the client

```

>>> from jrpc import SimpleTCPClient
>>> conn = SimpleTCPClient("myserver.com", 9999, ssl=True)
>>> dir(conn)
[u'check_process', u'cpuinfo', u'disk_usage', 'get', u'get_env', 'geturl', u'ifconfig', u'iostat', u'list_methods', u'meminfo', u'method_help', u'method_signature', u'mount', u'ping', 'post', u'running_process', u'uptime']
>>> conn.ping()
'{"ping": "pong"}'
>>> conn.list_methods()
'{"list_methods": ["check_process", "cpuinfo", "disk_usage", "get_env", "ifconfig", "iostat", "list_methods", "meminfo", "method_help", "method_signature", "mount", "ping", "running_process", "uptime"]}'
>>> conn.method_help("ping")
'{"method_help": ":return: response to ping"}'
>>> conn.method_help("check_process")
'{"method_help": ":param process\\n:return usage of the process on the system\\n:return {\\"output\\": <array>, \\"error\\": error}"}'

```

Every registered method on the server will automatically show in the client

### JSON Format

If you are using your own client, the json format would matter as the server is expecting the GET/POST in a certain key, value pair.
Your key would be the name of the method and the value would be the parameters/arguments that needs to passed to that method

For example:

```

example 1: {"method_name": "param"}

# if it requires more than one - order matters
example 2: {"method_name": ["param1", "param2"] }

# if you know the param names then order doesnt matter
example 3: {"method_name": {"param1": "param1", "param2": "param2"} }

# for example
$ curl --insecure -X POST https://myserver.com:9999 -d '{"check_process": "python"}' | python -mjson.tool
$ curl --insecure -X POST https://myserver.com:9999 -d '{"check_process": ["python"]}' | python -mjson.tool
$ curl --insecure -X POST https://myserver.com:9999 -d '{"check_process": {"process":"python"}}' | python -mjson.tool
