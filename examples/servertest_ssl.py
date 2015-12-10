import ssl

from jrpcServer.SimpleTCPServer import SimpleTCPServer

def ping():
  return "pong"

def blah(a):
  return a

if __name__ == "__main__":
  HOST, PORT = "localhost", 9999
  server = Server((HOST, PORT))
  server.socket = ssl.wrap_socket(server.socket, keyfile='key.pem', certfile='cacert.pem', server_side=True)
  server.register_function( ping )
  server.register_function( blah )
  server.serve_forever()
