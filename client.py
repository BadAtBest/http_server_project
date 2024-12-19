"""
Version 3.0: Multi-connection client using the socketserver module.
This client connects multiple sockets to the server simultaneously, sends predefined messages, 
and reads server responses for each connection.
"""

import socket
import sys

def start_connection(host, port, num_conns): # Can connect to server with multiple sockets.
    for i in range(num_conns):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                message = f"Hello from client {i + 1}"  # Create a string message
                s.sendall(message.encode())  # Convert the string to bytes before sending
                data = s.recv(1024)  # Receive the echoed response as bytes
                print(f"Client {i + 1}: Received: {data.decode()}")  # Decode bytes back to string
        except Exception as e:
            print(f"Client {i + 1}: Connection failed with error: {e}")

if len(sys.argv) != 4:  # Ensure proper command-line arguments are provided
    print(f"Usage: {sys.argv[0]} <host> <port> <num_connections>")
    sys.exit(1)

host, port, num_conns = sys.argv[1:4]
start_connection(host, int(port), int(num_conns))