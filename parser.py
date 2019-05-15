import argparse

"""
Argument parser for both the client and server program.
"""
def parser():
    parser = argparse.ArgumentParser(description='A simple python chatroom server/client')
    parser.add_argument('-ip', '--ip_address', help="Ip adress for the server.", default="127.0.0.1")
    parser.add_argument('-port', '--port_number', type=int,  help="Port number for the server.", default=6000)
    
    return parser.parse_args()

# for testing
if __name__ == "__main__":
    print(parser())
