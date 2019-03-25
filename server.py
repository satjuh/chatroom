from socket import socket, AF_INET, SOCK_STREAM, timeout
from threading import Thread, current_thread
from datetime import datetime
import signal

list_of_clients = []
threads = []
TIMEOUT = 10

# Included while testing
# Later argv parameters
HOST = "127.0.0.1"
PORT = 6000
alive = True

# Print message to log
def log_print(msg):
    print(datetime.now().time(), msg)

# ctrl + c signal handler
def sigint(sig, frame):
    log_print("Shutting down the server...")
    global alive
    alive = False

# Sender = the sender of the message
# msg = message to be sent in bytes "utf-8"
# name = name of the sender in bytes "utf-8"
def broadcast(sender, msg, name):
    for client in list_of_clients:
        if client != sender:
            space = bytes(" ", "utf-8")
            client.send(name + space + msg)


def remove_connection(conn, addr):
    if conn in list_of_clients:
        list_of_clients.remove(conn)
        log_print("Connection " + str(addr[0]) + " " + str(addr[1]) + " closed.")

def remove_thread(thread):
    if thread in threads:
        threads.remove(thread)

def service_client(conn, addr):
    welcome = "Welcome to the chatroom"
    conn.send(welcome.encode())
    conn.settimeout(TIMEOUT)
    while alive:
        try:
            msg = conn.recv(2048)
            if msg:
                broadcast(conn, msg, bytes(addr[0], "utf-8"))
            else:
                conn.close()
                remove_connection(conn, addr)
                remove_thread(current_thread())
                break
        except timeout:
            continue


def main():
    try:
        log_print("Starting the server with " + str(HOST) + " " + str(PORT))
        with socket(AF_INET, SOCK_STREAM) as server:
            server.bind((HOST, PORT))
            server.listen()
            server.settimeout(TIMEOUT)
            while alive:
                try:
                    conn, addr = server.accept()
                    log_print("Ip" + str(addr[0]) + " port: " + str(addr[1]) + " connected")
                    list_of_clients.append(conn)
                    t = Thread(target=service_client, args=[conn, addr])
                    threads.append(t)
                    t.start()
                except timeout:
                    continue

        #Telling users that the server is shuttind down
        for client in list_of_clients:
            msg = "Server closing...".encode()
            client.send(msg)
        # Joining threads to close the server
        for thread in threads:
            thread.join()

        log_print("Server shutdown")

    except OSError:
        log_print("Adress already in use")





if __name__ == "__main__":
    # Signal handler for stopping the server
    signal.signal(signal.SIGINT, sigint)
    main()
