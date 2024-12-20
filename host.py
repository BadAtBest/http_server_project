"""
Version 3.0: Multi-client TCP echo server using socketserver.
"""

import socketserver
import sys
import os

class MyHandler(socketserver.BaseRequestHandler):
    def handle(self):  # Overriding handle
        print(f"Connected by {self.client_address}")
        data = self.request.recv(1024).decode()
        if data:
            print(f"Received: {data.strip()}")
        request_line = data.split("\r\n")[0]
        split_data = request_line.split()
        request = split_data[0]
        path = split_data[1].lstrip("/")
        if path == "": # Default file 
            path = "index.html"
        file_path = f"static/{path}"
        if os.path.exists(file_path):
            if request == "GET":
                with open(file_path, "rb") as f:
                    file_content = f.read()

                content_type = "text/html" if file_path.endswith(".html") else "application/octet-stream"
                response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: {content_type}\r\n"
                    f"Content-Length: {len(file_content)}\r\n"
                    f"\r\n"
                ).encode() + file_content # Combines headers and file content
                self.request.sendall(response)
        else:
            error_message = "Error 404: File not found"
            response = (
                f"HTTP/1.1 404 Not Found\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(error_message)}\r\n"
                f"\r\n"
                f"{error_message}"
            )
            self.request.sendall(response.encode())

if len(sys.argv) != 3:  # Ensures correct command-line arguments are provided
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