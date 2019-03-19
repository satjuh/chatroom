from threading import Thread
import socket
from tkinter import *



class Gui(Tk):
    def __init__(self):
        Tk.__init__(self)
        # Frame that houses scroll bar and msg_list
        self.frame = Frame(self)
        self.scrollbar = Scrollbar(self)
        self.msg_list = Listbox(self.frame, height=50, width = 100, yscrollcommand=self.scrollbar.set)

        # Input box for reading user input and saving it to self.msg variable
        self.msg = StringVar()
        self.input_box = Entry(self, textvariable=self.msg)
        self.input_box.bind("<Return>", self.send)

        # Buttons for closing and sending
        self.close_button = Button(self, text="Quit", command=quit)
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
        self.msg_list.insert(END, self.msg.get())
        self.msg.set("")

    def quit(self):
        self.destroy()





if __name__ == "__main__":
    app = Gui()
    app.mainloop()
