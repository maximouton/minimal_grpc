import os
from concurrent import futures
import logging
import signal
import sys
import tempfile
from venv import logger

from grpc_reflection.v1alpha import reflection

import logging
import logging_loki
from contextlib import redirect_stderr, redirect_stdout


import hello_pb2, hello_pb2_grpc
from hello_service import GreeterServicer

# ✅ Initialize Loki logging handler
loki_handler = logging_loki.LokiHandler(
    url="https://logs.cockpit.fr-par.scw.cloud/loki/api/v1/push",
    tags={"job": "data_access_gRPC"},
    auth=("8a1b326e-8a76-4ce3-a599-629bf0787c08", "4q1WRLlbWGTOMfzFFcP38ifNeKV2hyi9XWJytUMp9oxMxmMcQ1wff4nGyYZlFuXk"),
    version="1",
)

# ✅ Main Python logger setup
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("gRPCServer")
logger.addHandler(loki_handler)
    
import grpc

def serve():
    try:

        # Initialize gRPC server with interceptors
        logger.debug("Initializing gRPC server with interceptors")
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=10),
            interceptors=[],
        )

        # Add Greeter service to the server
        hello_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
        
        # Enable server reflection
        logger.debug("Enabling server reflection")
        SERVICE_NAMES = (
            hello_pb2.DESCRIPTOR.services_by_name["Greeter"].full_name,  # Correct reference to DESCRIPTOR
            reflection.SERVICE_NAME,  # Required to enable reflection
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)

        # Verify that the files are correctly filled with data
        with open("./dataaccessdev.planifique.eu-key.pem", "r") as key_file:
            key_data = key_file.read()
            logger.debug(f"key_data: {key_data}")
        with open("./dataaccessdev.planifique.eu-crt.pem", "r") as crt_file:
            crt_data = crt_file.read()
            logger.debug(f"crt_data: {crt_data}")

        # Create server credentials
        server_credentials = grpc.ssl_server_credentials((
            (open('./dataaccessdev.planifique.eu-key.pem', 'rb').read(), open('./dataaccessdev.planifique.eu-crt.pem', 'rb').read()),
        ))
        logger.debug("Attempting to add secure port")
        server.add_secure_port("[::]:54329", server_credentials)
        logger.info("gRPC server running in production mode on HTTPS port 54329")


        # Graceful shutdown
        def shutdown_grpc_server(*args):
            logger.info(f"Shutting down gRPC server... {args}")
            server.stop(0)
            logger.info("gRPC server shut down successfully")
            sys.exit(0)

        signal.signal(signal.SIGINT, shutdown_grpc_server)
        signal.signal(signal.SIGTERM, shutdown_grpc_server)

        logger.debug("Starting gRPC server")
        server.start()
        server.wait_for_termination()
    except Exception as e:
        logger.error(f"An error occurred while running the gRPC server: {e}", exc_info=True)
        logger.debug("Exception details", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    serve()
