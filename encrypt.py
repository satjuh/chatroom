from Crypto.Cipher import AES

# Hard coded key values for testing:

counter = "H" * 16
key = "H" * 32

def encrypt(msg):
    enc = AES.new(key, AES.MODE_CTR, counter=lambda: bytes(counter, "utf-8"))
    return enc.encrypt(msg)

def decrypt(msg):
    dec = AES.new(key, AES.MODE_CTR, counter=lambda: bytes(counter, "utf-8"))
    return dec.decrypt(msg)
