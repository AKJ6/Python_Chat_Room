import queue
import socket
import threading
import ssl

messages = queue.Queue()
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))  # Binding to all available network interfaces

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain(certfile="server.crt", keyfile="server.key")

def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except Exception as e:
            print("Error receiving message:", e)

def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            print(message.decode())
            if addr not in clients:
                clients.append(addr)
            for client in clients:
                try:
                    if message.decode().startswith("SIGNUP_TAG:"):
                        name = message.decode()[message.decode().index(":") + 1:]
                        # Exclude sending the signup message back to the sender
                        if client != addr:
                            server.sendto(f"{name} joined!".encode(), client)
                    else:
                        # Exclude sending the message back to the sender
                        if client != addr:
                            server.sendto(message, client)
                except Exception as e:
                    print("Error broadcasting message:", e)
                    clients.remove(client)

t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)
t1.start()
t2.start() 
