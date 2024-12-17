import socket
import selectors
import sys
import types

"""
Version 2.0: Multi-connection client using the selector module.
This client connects multiple sockets to the server simultaneously, sends predefined messages, 
and reads server responses for each connection.
"""

sel = selectors.DefaultSelector()

# Predefined messages to send to the server
messages = [b"Message 1", b"Message 2"]


def start_connection(host, port, num_conns):
    """
    Starts the specified number of connections to the server.

    Args:
        host (str): The server's host or IP address.
        port (int): The server's port number.
        num_conns (int): Number of client connections to establish.
    """
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print(f"Starting connection {connid} to {server_addr}")
        
        # Create a non-blocking socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)  # Non-blocking connection attempt
        
        # Monitor both read and write events for this connection
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        
        # Track the state of this connection
        data = types.SimpleNamespace(
            connid=connid,              # Connection ID
            msg_total=sum(len(m) for m in messages),  # Total bytes to send
            recv_total=0,               # Total bytes received so far
            messages=messages.copy(),   # Copy of the messages for this connection
            outb=b""                    # Outgoing buffer (empty initially)
        )
        
        # Register the socket with the selector
        sel.register(sock, events, data=data)


def service_connection(key, mask):
    """
    Handles communication with a specific connection when it is ready for I/O.

    Args:
        key: The `SelectorKey` for the connection.
        mask: The event mask indicating whether the socket is ready to read/write.
    """
    sock = key.fileobj  # The socket being monitored
    data = key.data     # The connection's state

    # Handle reading if the socket is ready to read
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Read up to 1024 bytes
        if recv_data:  # If data is received, print it and update the received total
            print(f"Received {recv_data!r} from connection {data.connid}")
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            # If no data received or all messages have been echoed back, close the connection
            print(f"Closing connection {data.connid}")
            sel.unregister(sock)
            sock.close()

    # Handle writing if the socket is ready to write
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:  # If there's no outgoing data, pop the next message
            data.outb = data.messages.pop(0)
        if data.outb:  # Send data if there's something in the outgoing buffer
            print(f"Sending {data.outb!r} to connection {data.connid}")
            sent = sock.send(data.outb)  # Send data
            data.outb = data.outb[sent:]  # Remove sent portion from the buffer


if len(sys.argv) != 4:  # Ensure proper command-line arguments are provided
    print(f"Usage: {sys.argv[0]} <host> <port> <num_connections>")
    sys.exit(1)

# Parse command-line arguments
host, port, num_conns = sys.argv[1:4]
start_connection(host, int(port), int(num_conns))

try:
    while True:
        events = sel.select(timeout=1)  # Wait for I/O events with a 1-second timeout
        if events:  # Process events if any are triggered
            for key, mask in events:
                service_connection(key, mask)  # Handle communication for each connection
        
        # Exit the loop when no sockets are being monitored
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()