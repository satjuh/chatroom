from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, timeout
from tkinter import *
from tkinter import font as tkFont
from parser import parser

# Own wrapper for encryption
from encrypt import decrypt_keys, generate_keys, encrypt_AES, decrypt_AES

# Set global alive variable for threads
alive = True

# Thread class for listening new messages
class Listen(Thread):
    def __init__(self, socket, app, password):
        Thread.__init__(self)
        self.socket = socket
        self.app = app
        self.password= password

    # Main functionality of listening thread 
    def run(self):
        server.settimeout(3)
        while alive:
            try:
                msg = self.socket.recv(2048)
                if msg:
                    decrypted = decrypt_AES(msg, self.password)
                    if decrypted:
                        Gui.insert_msg(self.app, decrypted.decode("utf-8"))

                if decrypted == "Server closing...":
                    break
            except timeout:
                continue
            except OSError:
                break

# Exchagen public key with the server in variable socket.
# socket = servers socket variable
def start_connection(socket):
    private, public = generate_keys()
    server.settimeout(5)
    for i in range(0, 5):
        try:
            server_publickey = socket.recv(2048)
            socket.send(public)
            if server_publickey:
                return private, server_publickey
        except timeout:
            pass
    return False, False

# Get AES encryption key from the server.
def exchange_password(socket, private):
    server.settimeout(5)

    for i in range(0, 5):
        try:
            password = decrypt_keys(socket.recv(2048), private)
            if password:
                socket.send(encrypt_AES("Test msg", password))
                return password
        except timeout:
            pass

# Class for the tkinter gui 
class Gui(Tk):
    def __init__(self, server, password):
        Tk.__init__(self)
        # Internal variables
        self.server = server
        self.password = password

        # Frame that houses scroll bar and msg_list
        self.frame = Frame(self)
        self.scrollbar = Scrollbar(self)
        self.msg_list = Listbox(self.frame, height=30, width=100, yscrollcommand=self.scrollbar.set)

        # Input box for reading user input and saving it to self.msg variable
        self.msg = StringVar()
        self.msg.trace("w", self.__callback)
        self.input_box = Entry(self, textvariable=self.msg, width=100)
        self.input_box.bind("<Return>", self.send)

        # Buttons for closing and sending
        self.close_button = Button(self, text="Quit", command=self.quit)
        self.send_button = Button (self, text="Send", command=self.send)

        # Packing
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.msg_list.pack(side=LEFT, fill=BOTH)
        self.msg_list.pack()
        self.frame.pack()
        self.input_box.pack()
        self.close_button.pack()
        self.send_button.pack()

    # To limit how much text is allowed to be typed into the entry field.
    def __callback(self, *dummy):
        value = self.msg.get()
        size = 2048
        if len(bytes(value,"utf-8")) >= size:
            self.msg.set(value[0:len(value)-1])

    # Send message to the server
    def send(self, event=NONE):
        msg = self.msg.get()
        self.insert_msg("<you> "+ msg)
        self.server.send(encrypt_AES(msg, self.password))
        self.msg.set("")

    # Quit program 
    def quit(self):
        encrypted = encrypt_AES("<username>" + " disconnected", self.password)
        self.server.send(encrypted)
        global alive
        alive = False
        self.destroy()

    # Insert message to the Qui in the correct item.
    def insert_msg(self, msg):
        self.msg_list.insert(END, msg)



if __name__ == "__main__":
    #default HOST = "127.0.0.1"
    args = parser()
    HOST = args.ip_address
    #default PORT = 6000
    PORT = args.port_number 
    try:

        # Initialize socket
        server = socket(AF_INET, SOCK_STREAM)
        server.connect((HOST, PORT))

        # Create encryption keys
        private, public = start_connection(server)
        password = exchange_password(server, private)

        if not private or not public:
            raise ConnectionAbortedError

        # Start the Gui
        app = Gui(server, password)

        # Starting the listening Thread
        t = Listen(server, app, password)
        t.start()
        app.mainloop()

        # Shutting down
        server.close()
        t.join()
    except ConnectionRefusedError:
        print("Server is not up on", HOST, PORT)

    except ConnectionAbortedError:
        print("Failed to create a secure connection with the server!")
