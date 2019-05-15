from socket import socket, AF_INET, SOCK_STREAM, timeout
from threading import Thread, current_thread, Lock
from datetime import datetime
from encrypt import encrypt_keys, generate_keys, decrypt_AES, encrypt_AES, create_encryptionkey
from parser import parser

import signal
import time


# Locking shared resources
lock = Lock()

# Global variables
list_of_clients = dict()
threads = []
TIMEOUT = 10

# Set global alive variable for threads
alive = True

"""
# Print message to log
# msg = msg to be printed
"""
def log_print(msg):
    print(datetime.now().time(), msg)

# ctrl + c signal handler
def sigint(sig, frame):
    log_print("Shutting down the server...")
    global alive
    alive = False

"""
# Sender = the sender of the message
# msg = message to be sent in bytes "utf-8"
# name = name of the sender in bytes "utf-8"
"""
def broadcast(sender, msg, name):
    with lock:
        for client in list(list_of_clients.keys()):
            if client != sender:
                send = name + "> " + msg
                client.send(encrypt_AES(send, list_of_clients[client]))

# Remove the given connection from dict.
def remove_connection(conn, addr):
    with lock:
        if conn in list(list_of_clients.keys()):
            del list_of_clients[conn]
            log_print("Connection " + str(addr[0]) + " " + str(addr[1]) + " closed.")

# Remove thread from thread pool
def remove_thread(thread):
    with lock:
        if thread in threads:
            threads.remove(thread)

# Set public and private keys with the client
def start_connection(conn):
    private, public = generate_keys()
    conn.settimeout(5)
    for i in range(0,5):
        try:
            conn.send(public)
            client_public = conn.recv(2048)

            if client_public:
                return client_public, private

        except timeout:
            pass

    return False, False

"""
# Exchange AES encryption key with client
# conn = client that the encryption key is to be sent
# public_key = clients public key used in encrypting the encryption key
"""
def exchange_pass(conn, public_key):
    conn.settimeout(5)
    password = create_encryptionkey()
    try:
        with lock:
            conn.send(encrypt_keys(password, public_key))
            msg = conn.recv(2048)
            if decrypt_AES(msg, password):
                list_of_clients[conn] = password
                return True
    except timeout:
        return False

"""
# Listen to clients messages and react when a message is received.
# conn = clients connection
# addr = clients andress information (ip, port etc...)
"""
def service_client(conn, addr):
    # Start the connection by exchanging public and private keys
    public_key, private = start_connection(conn)

    if not public_key or not private:
        conn.close()
        remove_connection(conn, addr)
        remove_thread(current_thread())
        return

    if not exchange_pass(conn, public_key):
        return

    with lock:
        password = list_of_clients[conn]
    welcome = "Welcome to the chatroom"
    conn.send(encrypt_AES(welcome, password))
    conn.settimeout(TIMEOUT)
    while alive:
        try:
            msg = conn.recv(2048)
            if msg:
                decrypted = decrypt_AES(msg, password).decode("utf-8")
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

        except UnicodeDecodeError:
            log_print("Connection " + str(addr[0]) + " " + str(addr[1]) + " sent a malformed message.")

        except BrokenPipeError:
            log_print("BrokenPipeError: One of threads has crashed:")
            continue


def main():
    # signal handler for stopping the server
    signal.signal(signal.SIGINT, sigint)
    
    args = parser()

    # Default HOST = "127.0.0.1"
    HOST = args.ip_address
    # Default PORT = 6000
    PORT = args.port_number

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
                    client.send(encrypt_AES(msg, list_of_clients[client]))

            # Joining threads to close the server
            for thread in threads:
                thread.join()

            log_print("Server shutdown")
            break

        except OSError:
            if alive:
                time.sleep(wait)
                wait = wait * 2
                log_print("Address already in use")

if __name__ == "__main__":
    main()
