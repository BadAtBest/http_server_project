"""
Version 3.0: Multi-connection client using the socketserver module.
This client connects multiple sockets to the server simultaneously, sends predefined messages, 
and reads server responses for each connection.
"""

import socket
import sys

def start_connection(host, port, request, path): # Can connect to server with multiple sockets.
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))

                http_request = ( # Constructing HTTP request 
                    f"{request.upper()} /{path} HTTP/1.1\r\n"
                    f"Host: {host}\r\n"
                    f"Connection: close\r\n" # Close the connection after the response
                    f"\r\n" 
                )
                
                s.sendall(http_request.encode())  # Convert the string to bytes before sending
                
                response = b"" #Receive the response
                while True:
                    data = s.recv(1024)
                    if not data:
                        break
                    response += data
                     
                print(f"Client: Received:\n {response.decode()}")  # Prints decoded response

        except Exception as e:
            print(f"Client: Connection failed with error: {e}")

if len(sys.argv) != 5:  # Ensure proper command-line arguments are provided
    print(f"Usage: {sys.argv[0]} <host> <port> <request> <path>")
    sys.exit(1)

host, port, request, path = sys.argv[1:5]

if request.upper() not in ["GET"]:
     print("Error: Unsupported HTTP method. Only GET is supported")
     sys.exit(1)

start_connection(host, int(port), request, path)