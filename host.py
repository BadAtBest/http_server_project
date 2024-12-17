import socket
import selectors
import sys
import types

"""
Version 2.0 http server, multi-client echo server using selectors.
"""

sel = selectors.DefaultSelector()
#When a new client connection is ready to be accepted.
def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False) #sets blocking for the new socket object to be false.
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
#fucntion called when client is ready for reading/writing.
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data

    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024) #client data.
        if recv_data:
            data.outb += recv_data
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    if mask & selectors.EVENT_WRITE:
        if data.outb: #If there is data to send.
            print(f"Echoing {data.outb!r} to {data.addr}")
            sent = sock.send(data.outb) #Send data to client.
            data.outb = data.outb[sent:] #Remove sent portion.

if len(sys.argv) != 3: #Defines command line requirements.
    print(f"Usage: {sys.argv[0]} <host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind(host, port)
lsock.listen()
print(f"Listening on {(host, port)}")
lsock.setblocking(False) #Makes server socket non-blocking.
sel.register(lsock, selectors.EVENT_READ, data=None) #Registers the server socket to monitor for EVENT_READ (new connection).

try:
    while True:
        events = sel.select(timeout=None) #Wait for event.
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj) #Accepts new connection.
            else:
                service_connection(key, mask) #Handle client comms.
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()