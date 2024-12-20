"""
Version 3.2: Enhanced HTTP client with improved input validation, default path handling,
and restructured for better modularity. The client supports GET and POST requests,
with persistent connection management for multiple requests over the same session.
"""

import socket
import sys


def start_connection(host, port, timeout=30):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.settimeout(timeout)
        return s
    except Exception as e:
        print(f"Client: Connection failed with error: {e}")
        sys.exit(1)

def send_http_request(s, http_request): # Problem
    try:
        print(f"Sending request:\n{http_request}")
        s.sendall(http_request.encode())
        response = b""
        data = s.recv(1024)
        print(f"Client: Received:\n{data.decode()}")
    except Exception as e:
        print(f"Error while sending request: {e}")

def handle_persistent_connection(s, host, connection_header):
    print("Persistent connection established. Enter new requests or 'exit' to close.")
    print("Examples: 'GET /index.html' or 'POST This is a test message'")
    while True:
        try:
            user_input = input("Enter HTTP request or 'exit':\n").strip()
            if user_input.lower() == "exit":
                print("Closing persistent connection.")
                break
            if user_input.upper().startswith("GET"):
                path = user_input.split()[1] if len(user_input.split()) > 1 else "index.html"
                print(f"Sending GET for path: {path}")
                GET(s, host, path, connection_header)
            elif user_input.upper().startswith("POST"):
                message = input("Enter the message to POST:\n").strip()
                print(f"Sending POST with message: {message}")
                POST(s, host, message, connection_header)
            else:
                print("Invalid request. Use 'GET <path>' or 'POST <message>'.")
        except Exception as e:
            print(f"Error during persistent connection: {e}")
            break

def GET(s, host, path, connection_header):
    """Send a GET request to the server."""
    if not path.strip():
        path = "index.html"  # Default file
    try:
        http_request = (
            f"GET /{path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Connection: {connection_header}\r\n"
            f"\r\n"
        )
        send_http_request(s, http_request)
    except Exception as e:
        print(f"Error in GET request: {e}")


def POST(s, host, message, connection_header):
    """Send a POST request to the server."""
    try:
        content_length = len(message)
        http_request = (
            f"POST /submit HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Content-Type: text/plain\r\n"
            f"Content-Length: {content_length}\r\n"
            f"Connection: {connection_header}\r\n"
            f"\r\n"
            f"{message}"
        )
        send_http_request(s, http_request)
    except Exception as e:
        print(f"Error in POST request: {e}")


try:
    if __name__ == "__main__":
        host = input("Enter the server host: ").strip()
        port = int(input("Enter the server port: ").strip())
        connection_header = input("Enter 'keep-alive' or 'close': ").strip().lower()
        method = input("Enter the HTTP method (GET or POST): ").strip().upper()

        s = start_connection(host, port)

        if method == "GET":
            path = input("Enter the file path (default: index.html): ").strip()
            GET(s, host, path, connection_header)

        elif method == "POST":
            message = input("Enter the message to POST: ").strip()
            POST(s, host, message, connection_header)

        else:
            print("Invalid method. Only GET and POST are supported.")
            sys.exit(1)

        if connection_header == "keep-alive":
                    handle_persistent_connection(s, host, "keep-alive")
        
except socket.timeout:
    print("Connection timed out. Please try again later.\n")
finally:
    print("\nShutting down client")
    s.close()