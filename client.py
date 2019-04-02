from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, timeout
from tkinter import *

# Own wrapper for encryption
from encrypt import decrypt, encrypt

# Included while testing
# Later argv parameters
HOST = "127.0.0.1"
PORT = 6000
alive = True

# Thread class for listening new messages
class Listen(Thread):
    def __init__(self, socket, app):
        Thread.__init__(self)
        self.socket = socket
        self.app = app

    def run(self):
        server.settimeout(3)
        while alive:
            try:
                msg = self.socket.recv(2048)
                decrypted = decrypt(msg).decode("utf-8")
                Gui.insert_msg(self.app, decrypted)

                if decrypted == "Server closing...":
                    break
            except timeout:
                continue
            except OSError:
                break


class Gui(Tk):
    def __init__(self, server):
        Tk.__init__(self)
        # Internal variables
        self.server = server

        # Frame that houses scroll bar and msg_list
        self.frame = Frame(self)
        self.scrollbar = Scrollbar(self)
        self.msg_list = Listbox(self.frame, height=30, width=100, yscrollcommand=self.scrollbar.set)

        # Input box for reading user input and saving it to self.msg variable
        self.msg = StringVar()
        self.input_box = Entry(self, textvariable=self.msg)
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

    def send(self, event=NONE):
        msg = self.msg.get()
        self.insert_msg(msg)
        self.server.send(encrypt(msg))
        self.msg.set("")

    def quit(self):
        encrypted = encrypt("<username>" + " disconnected")
        self.server.send(encrypted)
        global alive
        alive = False
        self.destroy()

    def insert_msg(self, msg):
        self.msg_list.insert(END, msg)



if __name__ == "__main__":
    try:

        # Initialize socket
        server = socket(AF_INET, SOCK_STREAM)
        server.connect((HOST, PORT))
        server.settimeout(3)

        # Start the Gui
        app = Gui(server)

        # Starting the listening Thread
        t = Listen(server, app)
        t.start()
        app.mainloop()

        # Shutting down
        server.close()
        t.join()
    except ConnectionRefusedError:
        print("Server is not up on", HOST, PORT)
