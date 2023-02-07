from concurrent import futures
import logging
import grpc
from proto import dhcp_pb2

class DHCP(dhcp_pb2._DHCP):

    def GetDHCPRange(self, request, context):
        return dhcp_pb2.Request(code=200, message="Here it is")

def serve():
    port = '5001'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    dhcp_pb2.add_DHCP_to_server(DHCP(), server)
    server.add_insecure_port('[::]:' + port)
    server.wait_for_termination()

logging.basicConfig()
serve()