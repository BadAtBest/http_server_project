"""
Version 3.0: Multi-client HTTP server using socketserver.
"""

import socketserver
import sys
import os

class MyHandler(socketserver.BaseRequestHandler):
    def handle(self):  # Overriding handle
        from datetime import datetime # To add timestamps to Post Logs

        print(f"Connected by {self.client_address}")
        data = self.request.recv(1024).decode()
        if not data:
            return
        print(f"Received: {data.strip()}")

        request_line = data.split("\r\n")[0] # Parse request
        header_and_body = data.split("\r\n\r\n", 1)
        header = header_and_body[0]
        body = header_and_body[1] if len(header_and_body) > 1 else ""

        try:
            method, path, _ = request_line.split()
        except ValueError:
            response = (
                f"HTTP/1.1 400 Bad Request\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: 11\r\n"
                f"\r\n"
                f"Bad Request\n"
            ).encode()
            self.request.sendall(response)
            return

        if path == "" or path == "/": # Default file 
            path = "index.html"
        file_path = f"static/{path}"

        

        if method == "GET": # IF GET request
            if os.path.exists(file_path): # If file path exists
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
            else: # If file path does not exist
                error_message = "Error 404: File not found"
                response = (
                    f"HTTP/1.1 404 Not Found\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(error_message)}\r\n"
                    f"\r\n"
                    f"{error_message}"
                )
                self.request.sendall(response.encode())

        elif method == "POST": # If POST request
            log_file = "logs/post_log.txt"
            with open(log_file, "a") as f:
                f.write(f"{datetime.now()} - {self.client_address}:\n")
                f.write(f"{body}\n")
                f.write("-" * 60 + "\n")

            response_message = "Data Logged"
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(response_message)}\r\n"
                f"\r\n"
                f"{response_message}"
            ).encode()
            self.request.sendall(response)

        else: # Unsupported method
            response = (
                f"HTTP/1.1 405 Method Not Allowed\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: 23\r\n"
                f"\r\n"
                f"Method Not Allowed\n"
            ).encode()
            self.request.sendall(response)

        

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