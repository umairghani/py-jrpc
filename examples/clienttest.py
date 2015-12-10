from jrpc import SimpleTCPClient

conn = SimpleTCPClient("localhost", 9999)
print conn.ping()
print conn.blah("test")
