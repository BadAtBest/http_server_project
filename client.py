import os
import socket 
#Default IP for internal network setup using Virtual Box, connection made between Desktop and VM.
HOST = os.getenv("HOST", "198.168.56.102")
PORT = int(os.getenv("PORT", 8080))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b"Hello, world")
    data = s.recv(1024)

print(f"Received {data!r}")