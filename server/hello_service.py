import grpc
from concurrent import futures
import hello_pb2_grpc
import hello_pb2

class GreeterServicer(hello_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        response = hello_pb2.HelloReply()
        response.message = f"Hello, {request.name}!"
        return response