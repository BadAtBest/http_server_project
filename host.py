"""
Version 3.0: Multi-client TCP echo server using socketserver.
"""

import socketserver
import sys

class MyHandler(socketserver.BaseRequestHandler):
    def handle(self):  # Overriding handle
        print(f"Connected by {self.client_address}")
        data = self.request.recv(1024)
        if data:
            print(f"Received: {data.decode().strip()}")
            self.request.sendall(data)

if len(sys.argv) != 3:  # Ensures correct command-line arguments are provided.
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True # Prevents "Address already in use" Error

try:
    server = ThreadedTCPServer((host, port), MyHandler)
    print(f"Starting server on {host}:{port}")
    server.serve_forever()  # Starts the server loop
except KeyboardInterrupt:
    print("\nShutting down the server.")
finally:
    server.shutdown()
    server.server_close()  # Releases the server's resources