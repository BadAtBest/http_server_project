import os
import socket 
#Default IP for internal network setup using Virtual Box, connection made between Desktop and VM.
HOST = os.getenv("HOST", "198.168.56.102")
PORT = int(os.getenv("PORT", 8080))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST,PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
            