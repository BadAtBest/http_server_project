"""
Version 3.2: Multi-client HTTP server with improved modularity, streamlined request handling,
enhanced logging for POST requests, and better handling of persistent connections.
This version isolates GET and POST logic into separate methods for clarity and maintainability.
"""

import socketserver
import sys
import os
from datetime import datetime
import ssl


class MyHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            print(f"Connected by {self.client_address}")
            data = self.request.recv(1024).decode()
            if not data:
                print("No data received. Closing connection.")
                return
            print(f"Received:\n{data.strip()}")

            request_line = data.split("\r\n")[0]
            header_and_body = data.split("\r\n\r\n", 1)
            header = header_and_body[0]
            body = header_and_body[1] if len(header_and_body) > 1 else ""

            if "Host" not in header:
                self.request.sendall(
                    b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\nContent-Length: 11\r\n\r\nBad Request\n"
                )
                break

            try:
                method, path, _ = request_line.split()
                method = method.upper()
            except ValueError:
                response = (
                    f"HTTP/1.1 400 Bad Request\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: 11\r\n"
                    f"\r\n"
                    f"Bad Request\n"
                ).encode()
                self.request.sendall(response)
                break

            # Default path for root requests
            if path == "/" or not path.strip():
                path = "index.html"

            if method == "GET":
                self.GET(path, request_line)
            elif method == "POST":
                self.POST(header, body, request_line)
            elif method == "OPTIONS":
                response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Allowed: GET, POST, OPTIONS\r\n"
                f"Content-Length: 0\r\n"
                f"\r\n"
            ).encode()
                self.request.sendall(response)
                self.log_request(request_line, "200 OK", "NONE")
            else:
                response = (
                    f"HTTP/1.1 405 Method Not Allowed\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: 23\r\n"
                    f"\r\n"
                    f"Method Not Allowed\n"
                ).encode()
                self.request.sendall(response)
                self.log_request(request_line, "405 Method Not Allowed", "Invalid request") # Call request log function

            connection_type = "close"
            for line in header.split("\r\n"):
                if line.lower().startswith("connection:"):
                    connection_type = line.split(":")[1].strip().lower()
                    break

            if connection_type != "keep-alive":
                print("Closing connection as requested.")
                break

    def GET(self, path, request_line):
        file_path = f"static/{path.lstrip('/')}"
        if os.path.isdir(file_path):
            file_path = os.path.join(file_path, "index.html")

        if ".." in path or path.startswith("/"):
            response = (
                f"HTTP/1.1 400 Bad Request\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: 11\r\n"
                f"\r\n"
                f"Bad Request\n"
            ).encode()
            self.request.sendall(response)
            self.log_request(request_line, "400 Bad Request", "Invalid path")
            return

        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                file_content = f.read()

            content_type = "text/html" if file_path.endswith(".html") else "application/octet-stream"
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(file_content)}\r\n"
                f"\r\n"
            ).encode() + file_content
            self.log_request(request_line, "200 OK", "NONE") # Call request log function
            self.request.sendall(response)
        else:
            error_message = "Error 404: File not found"
            response = (
                f"HTTP/1.1 404 Not Found\r\n"
                f"Content-Type: text/plain\r\n"
                f"Content-Length: {len(error_message)}\r\n"
                f"\r\n"
                f"{error_message}"
            ).encode()
            self.request.sendall(response)
            self.log_request(request_line, "404 File not found", "Invalid file address") # Call request log function

    def POST(self, header, body, request_line):
        if len(header) > 8192:  # 8 KB limit for headers
            self.request.sendall(
                b"HTTP/1.1 413 Payload Too Large\r\nContent-Type: text/plain\r\nContent-Length: 19\r\n\r\nPayload Too Large\n"
            )
            self.log_request(request_line, "413 Payload Too Large", "Invalid header size, too large") # Call request log function
            return

        content_length = 0
        for line in header.split("\r\n"):
            if line.lower().startswith("content-length:"):
                content_length = int(line.split(":")[1].strip())
                break

        if content_length == 0 or not body.strip():
            self.request.sendall(
                b"HTTP/1.1 411 Length Required\r\nContent-Type: text/plain\r\nContent-Length: 15\r\n\r\nLength Required\n"
            )
            self.log_request(request_line, "411 Length Required", "Post request with no content") # Call request log function
            return

        if content_length > 0 and len(body) != content_length:
            self.request.sendall(
                b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\nContent-Length: 11\r\n\r\nBad Request\n"
            )
            self.log_request(request_line, "400 Bad Request", "Content length does not match message") # Call request log function
            return
        
        MAX_BODY_SIZE = 1048576  # 1 MB
        if len(body.encode('utf-8')) > MAX_BODY_SIZE:
            self.request.sendall(
                b"HTTP/1.1 413 Payload Too Large\r\nContent-Type: text/plain\r\nContent-Length: 19\r\n\r\nPayload Too Large\n"
            )
            self.log_request(request_line, "413 Payload Too Large", "Body exceeds max size")
            return

        log_file = "logs/post_log.txt"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
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
        self.log_request(request_line, "200 OK", "NONE") # Call request log function

    def log_request(self, request_line, status, error):
        request_log_file = "logs/request_log.txt"
        client_ip = self.client_address[0] if isinstance(self.client_address, tuple) else self.client_address
        os.makedirs(os.path.dirname(request_log_file), exist_ok=True)
        with open(request_log_file, "a") as f:
            f.write(f"{datetime.now().isoformat()} Client: {client_ip} | Request: {request_line} | Status: {status} | Error: {error}\r\n")

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH) # For HTTPS
context.load_cert_chain(certfile="ssl/cert.pem", keyfile="ssl/key.pem")

try:
    server = ThreadedTCPServer((host, port), MyHandler)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    print(f"Starting server on {host}:{port}")
    server.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down the server.")
finally:
    server.shutdown()
    server.server_close()