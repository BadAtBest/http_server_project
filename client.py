"""
Version 3.0: HTTP client using the socketserver module.
This client connects to server and sends GET or POST request.
"""

import socket
import sys

def start_connection(host, port, request, path): # Can connect to server with multiple sockets.
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                if request == "GET": # GET request
                    http_request = ( # Constructing HTTP request 
                        f"{request} /{path} HTTP/1.1\r\n"
                        f"Host: {host}\r\n"
                        f"Connection: close\r\n" # Close the connection after the response
                        f"\r\n" 
                    )
                else: # POST request
                    http_request = ( # Constructing HTTP request 
                        f"{request} /submit HTTP/1.1\r\n"
                        f"Host: {host}\r\n"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Length: {len(path)}\r\n"
                        f"Connection: close\r\n"
                        f"\r\n"
                        f"{path}" # Message
                    )
                
                s.sendall(http_request.encode())  # Convert the string to bytes before sending
                
                response = b"" #Receive the response
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    response += data
                     
                print(f"Client: Received:\n{response.decode()}")  # Prints decoded response

        except Exception as e:
            print(f"Client: Connection failed with error: {e}")

if len(sys.argv) != 5:  # Ensure proper command-line arguments are provided
    print(f"Usage: {sys.argv[0]} <host> <port> <request> <path or message>")
    sys.exit(1)

host, port, request, path = sys.argv[1:5]  # path variable filled with message for POST requests
request = request.upper()

if request not in ["GET", "POST"]:
    print("Error: Unsupported HTTP method. Only GET and POST are supported")
    sys.exit(1)

if request == "POST" and not path.strip():
    print("Warning: No data provided for POST request body.")
    sys.exit(1)

start_connection(host, int(port), request, path)