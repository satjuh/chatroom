from socket import socket, AF_INET, SOCK_STREAM, timeout
from threading import Thread, current_thread, Lock
from datetime import datetime
from encrypt import encrypt, decrypt, generate_keys
from Crypto.PublicKey import RSA

import signal
import time


# Locking shared resources
lock = Lock()

# Global variables
list_of_clients = dict()
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
    with lock:
        for client in list(list_of_clients.keys()):
            if client != sender:
                send = name + "> " + msg
                client.send(encrypt(send, list_of_clients[client]))


def remove_connection(conn, addr):
    with lock:
        if conn in list(list_of_clients.keys()):
            del list_of_clients[conn]
            log_print("Connection " + str(addr[0]) + " " + str(addr[1]) + " closed.")

def remove_thread(thread):
    with lock:
        if thread in threads:
            threads.remove(thread)


def start_connection(conn, addr):
    private, public = generate_keys()
    conn.settimeout(3)
    try:
        conn.send(public)
        client_public = conn.recv(2048)

        if client_public:
            with lock:
                list_of_clients[conn] = client_public
                return client_public, private
        else:
            return False, False
    except timeout:
        return False, False


def service_client(conn, addr):
    # Start the connection by exchanging public and private keys
    public_key, private = start_connection(conn, addr)

    if not public_key or not private:
        conn.close()
        remove_connection(conn, addr)
        remove_thread(current_thread())
        return

    welcome = "Welcome to the chatroom"
    conn.send(encrypt(welcome, public_key))
    conn.settimeout(TIMEOUT)
    while alive:
        try:
            msg = conn.recv(2048)
            if msg:
                decrypted = decrypt(msg, private).decode("utf-8")
                broadcast(conn, decrypted, str(addr[0]))
            else:
                conn.close()
                remove_connection(conn, addr)
                remove_thread(current_thread())
                break


        except timeout:
            continue

        except ConnectionResetError:
            conn.close()
            remove_connection(conn, addr)
            remove_thread(current_thread())
            log_print("Connection " + str(addr[0]) + " " + str(addr[1]) + " closed.")
            break

        except BrokenPipeError:
            log_print("PipeError: why I don't know?")
            continue


def main():
    wait = 1

    while alive:
        try:
            log_print("Trying to start the server with " + str(HOST) + " " + str(PORT))
            with socket(AF_INET, SOCK_STREAM) as server:
                server.bind((HOST, PORT))
                server.listen()
                server.settimeout(TIMEOUT)
                log_print("Server started with " + str(HOST) + " " + str(PORT))
                while alive:
                    try:
                        conn, addr = server.accept()
                        log_print("Ip" + str(addr[0]) + " port: " + str(addr[1]) + " connected")
                        with lock:
                            list_of_clients[conn] = ""
                        t = Thread(target=service_client, args=[conn, addr])
                        threads.append(t)
                        t.start()
                    except timeout:
                        continue

            # Telling users that the server is shutting down
            with lock:
                for client in list(list_of_clients.keys()):
                    msg = "Server closing..."
                    client.send(encrypt(msg, list_of_clients[client]))

            # Joining threads to close the server
            for thread in threads:
                thread.join()

            log_print("Server shutdown")
            break

        except OSError:
            time.sleep(wait)
            wait = wait * 2
            log_print("Address already in use")

if __name__ == "__main__":
    # Signal handler for stopping the server
    signal.signal(signal.SIGINT, sigint)
    main()
