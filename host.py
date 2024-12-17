import socket
import selectors
import sys
import types

"""
Version 2.0: Multi-client TCP echo server using selectors.
"""

sel = selectors.DefaultSelector()

# When a new client connection is ready to be accepted.
def accept_wrapper(sock):
    conn, addr = sock.accept()  # Accept the new connection.
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)  # Sets the new client socket to non-blocking mode.
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")  # Track client buffers.
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

# Function called when client is ready for reading/writing.
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Client data.
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")  # Client disconnected.
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb:  # If there is data to send.
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb)  # Send data to client.
            data.outb = data.outb[sent:]  # Remove sent portion.

if len(sys.argv) != 3:  # Ensures correct command-line arguments are provided.
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Fix for "Address already in use"
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False)  # Makes server socket non-blocking.
sel.register(lsock, selectors.EVENT_READ, data=None)  # Monitor for new connections.

try:
    while True:
        events = sel.select(timeout=None)  # Wait for I/O events.
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)  # Accepts new connection.
            else:
                service_connection(key, mask)  # Handle client communications.
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()