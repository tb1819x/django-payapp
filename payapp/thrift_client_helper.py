"""
Client server for communicating with the thrift timestamp service

The module connects to the remote remote Thrift server running on port 10000 
and retrieves the current timestamp for transaction records
"""
import sys

sys.path.append("gen-py")

from timestamp_service import TimestampService
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol

def get_remote_timestamp():
    """
    - creates socket connection to local thrift sever
    - wraps transport for efficient communication
    - Use binary protocol for data exchange
    - create client to call the service
    - open connection and request timestamp
    Return: timestamp 
    """
    transport = TSocket.TSocket("127.0.0.1", 10000)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    client = TimestampService.Client(protocol)

    transport.open()
    timestamp = client.getCurrentTimestamp()
    transport.close()

    return timestamp