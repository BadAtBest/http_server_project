"""
Version 3.0: HTTP client using socketserver.
This client connects to a server and sends GET or POST requests, with persistent connection support.
"""

import socket
import sys


def start_connection(host, port, request, path, connection_header):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.settimeout(30)  # Set a 30-second timeout for the initial request

            # Construct the initial request
            if request == "GET":
                if not path.strip():
                    path = "index.html"  # Default path for GET requests
                http_request = (
                    f"{request} /{path} HTTP/1.1\r\n"
                    f"Host: {host}\r\n"
                    f"Connection: {connection_header}\r\n"
                    f"\r\n"
                )
            else:  # POST request
                message = path.strip()
                content_length = len(message)
                http_request = (
                    f"{request} /submit HTTP/1.1\r\n"
                    f"Host: {host}\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {content_length}\r\n"
                    f"Connection: {connection_header}\r\n"
                    f"\r\n"
                    f"{message}"
                )

            # Send the initial request
            s.sendall(http_request.encode())
            response = b""
            while True:
                data = s.recv(1024)
                if not data:
                    break
                response += data
            print(f"Client: Received:\n{response.decode()}")

            # Handle persistent connections
            if connection_header.lower() == "keep-alive":
                print(f"Persistent connection established. Enter new requests or 'exit' to close.")
                print("Example for GET: 'GET /index.html'")
                print("Example for POST: 'POST /submit'")
                while True:
                    s.settimeout(30)  # 30-second timeout for inactivity
                    user_response = input("Enter HTTP request and path/message or 'exit':\n").strip()

                    if user_response.lower() == 'exit':
                        print("Closing persistent connection.")
                        break

                    if not user_response.upper().startswith(("GET", "POST")):
                        print("Error: Request must start with 'GET' or 'POST'.")
                        continue

                    if user_response.upper().startswith("POST"):
                        message = input("What is the message you would like to POST:\n").strip()
                        content_length = len(message)
                        user_response += (
                            f"\r\nContent-Type: text/plain\r\n"
                            f"Content-Length: {content_length}\r\n"
                            f"\r\n"
                            f"{message}"
                        )
                    elif user_response.upper().startswith("GET"):
                        user_response += "\r\nConnection: keep-alive\r\n"

                    s.sendall(user_response.encode())
                    response = b""
                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        response += data
                    print(f"Client: Received:\n{response.decode()}")

    except Exception as e:
        print(f"Client: Connection failed with error: {e}")


if len(sys.argv) not in [5, 6]:
    print("Usage for POST: python client.py <host> <port> POST <keep-alive or close>")
    print("Usage for GET: python client.py <host> <port> GET <path> <keep-alive or close>")
    sys.exit(1)

host, port, request = sys.argv[1:4]
request = request.upper()

if request == "POST":
    connection_header = sys.argv[4]
    path = input("Enter the message you would like to POST:\n").strip()
    if not path:
        print("Error: POST request must include a body.")
        sys.exit(1)
elif request == "GET":
    if len(sys.argv) != 6:
        print("Usage: python client.py <host> <port> GET <path> <keep-alive or close>")
        sys.exit(1)
    path, connection_header = sys.argv[4:6]
else:
    print("Error: Unsupported HTTP method. Only GET and POST are supported.")
    sys.exit(1)

if connection_header.lower() not in ["keep-alive", "close"]:
    print(f"Error: Invalid connection header '{connection_header}'. Must be 'keep-alive' or 'close'.")
    sys.exit(1)

start_connection(host, int(port), request, path, connection_header)