from socket import socket, AF_INET, SOCK_STREAM, timeout
from threading import Thread
from datetime import datetime

list_of_clients = []

# Included while testing
# Later argv parameters
HOST = "127.0.0.1"
PORT = 6000
alive = True

def broadcast(sender, msg, name):
    for client in list_of_clients:
        if client != sender:
            client.send(name.encode + msg)

def service_client(conn, addr):
    welcome = "Welcome to the chatroom"
    conn.send(welcome.encode())
    conn.settimeout(30)
    """
    while alive:
        try:
            msg = conn.recv(2048)
            broadcast(conn, msg, addr)
        except timeout:
            continue
    """

# Save to log who connected and when.
def log_print(msg):
    print(datetime.now().time(), msg)

def main():
    print("Staring the server with", HOST, PORT)
    with socket(AF_INET, SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        while True:
            conn, addr = server.accept()
            log_print(addr)
            list_of_clients.append(addr)
            t = Thread(target=service_client(conn, addr), args=[conn, addr])
            t.start()
            t.join()





if __name__ == "__main__":
    main()
