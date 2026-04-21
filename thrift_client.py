"""
This module creates a socket connection to Thrift server
- wraps the transport for efficient communication
- uses binary protocol for data exchange
- creates client to call timestampservice
- opens connection to server
- call remote method to get current timestamp
"""

import sys

sys.path.append("gen-py")
from timestamp_service import TimestampService
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

transport = TSocket.TSocket("127.0.0.1", 10000)
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

client = TimestampService.Client(protocol)

transport.open()

timestamp = client.getCurrentTimestamp()
print("Timestamp from server:", timestamp)