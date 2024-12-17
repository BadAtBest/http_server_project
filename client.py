import socket 
import selectors
import sys
import types

"""
Version 2.0 http server, multi-connection client using selector module.
Client can connect mulitple sockets to server simultaniously, sends predefined messages, and
reads server response.
"""

sel = selectors.DefaultSelector()
messages = [b"Message 1", b"Message 2"] #The predetermined messages to be sent to the server.

def start_connection(host, port, num_conns): #Method to start connection to the server.
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=messages.copy(),
            outb=b""
        )
        sel.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj #The socket being monitored.
    data = key.data #Connection state.
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data: #If data is recieved prints it.
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.message:
            data.outb = data.messages.pop(0)
        if data.outb:
            print(f"Sending {data.outb!r} to connect {data.connid}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

if len(sys.argv) != 4: #Defines command line requirements.
    print(f"Usage: {sys.argv[0]} <host> <port> <num_connections>")
    sys.exit(1)
host, port, num_conns = sys.argv[1:4]
start_connection(host, int(port), int(num_conns))

try: 
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask) #Handles all connections.
        if not sel.get_map(): #When no sockets left loop breaks.
            break
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()