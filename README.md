# chatroom
A simple python chatroom with server and qui client

## Getting started:

To run the client use python3 and install pycrypto library that is needed for the
encryption. Pycroptodome should also work and is still receiving updates.

To run the server use python3 and install pycrypto or cryptodome (should work).

## How it works:

The chatroom is using server client model as it's base.
Low level sockets are used for communication between the server and the client.
The client is simple tkinter ui that will display messages received from the server. 
All communication between the server and the clients are encrypted by first exchanging 
a public key to send server generated random password and then using AES encryption
for further communication. 
