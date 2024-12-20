"""
Version 3.1: Multi-client HTTP server using socketserver with enhanced error handling,
support for persistent sessions, and improved compliance with HTTP standards.
"""

import socketserver
import sys
import os
from datetime import datetime

class MyHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            print(f"Connected by {self.client_address}")
            data = self.request.recv(1024).decode()
            if not data:
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
            file_path = f"static/{path.lstrip('/')}"

            if method == "GET":
                self.GET(file_path)

            elif method == "POST":
                self.POST(header, body)

            else:
                response = (
                    f"HTTP/1.1 405 Method Not Allowed\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: 23\r\n"
                    f"\r\n"
                    f"Method Not Allowed\n"
                ).encode()
                self.request.sendall(response)

            # Check Connection header for keep-alive or close
            connection_type = "close"  # Default behavior
            for line in header.split("\r\n"):
                if line.lower().startswith("connection:"):
                    connection_type = line.split(":")[1].strip().lower()
                    break

            if connection_type == "close":
                print("Closing connection as requested.")
                break

    def GET(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                file_content = f.read()

            content_type = "text/html" if file_path.endswith(".html") else "application/octet-stream"
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(file_content)}\r\n"
                f"\r\n"
            ).encode() + file_content
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

    def POST(self, header, body):
        if len(header) > 8192:  # 8 KB limit for headers
            self.request.sendall(
                b"HTTP/1.1 413 Payload Too Large\r\nContent-Type: text/plain\r\nContent-Length: 19\r\n\r\nPayload Too Large\n"
            )
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
            return

        if content_length > 0 and len(body) != content_length:
            self.request.sendall(
                b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/plain\r\nContent-Length: 11\r\n\r\nBad Request\n"
            )
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

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

try:
    server = ThreadedTCPServer((host, port), MyHandler)
    print(f"Starting server on {host}:{port}")
    server.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down the server.")
finally:
    server.shutdown()
    server.server_close()