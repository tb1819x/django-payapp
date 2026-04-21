"""
This module implements the Thrift timestamp server.

It:
- loads generated Thrift service code
- defines a handler to return the current timestamp
- sets up a server socket on port 10000
- uses buffered transport and binary protocol for communication
- listens for incoming requests and responds with timestamps
"""
import sys
import time

sys.path.append("gen-py")

from timestamp_service import TimestampService
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class TimestampHandler:
    def getCurrentTimestamp(self):
        return int(time.time())

handler = TimestampHandler()
processor = TimestampService.Processor(handler)

transport = TSocket.TServerSocket(host="127.0.0.1", port=10000)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

print("thrift timestamp server running on port 10000...")
server.serve()