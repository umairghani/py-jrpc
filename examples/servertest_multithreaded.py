from jrpcServer.SimpleTCPServer import SimpleTCPServer
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
  server.serve_forever()
