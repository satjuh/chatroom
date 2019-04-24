from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Util import Counter
from os import urandom


"""
Encrypts the message for the client with the given publickey
msg = message to be encrypted
publickey = publickey used in encryption as received from generate_keys
return bytes
"""
def encrypt_keys(msg, publickey):
    if isinstance(msg, str):
        msg = bytes(msg, "utf-8")
    key = RSA.importKey(publickey, passphrase=None)
    cipher = PKCS1_OAEP.new(key)
    ciphertext = cipher.encrypt(msg)
    return ciphertext

"""
Decrypts msg with the user private RSA key
msg = message to decrypted
privatekey = users private key
returns bytes
"""
def decrypt_keys(msg, privatekey):
    try:
        cipher = PKCS1_OAEP.new(privatekey)
        ciphertext = cipher.decrypt(msg)
        return ciphertext
    except ValueError:
        return False

"""
Generate both the private and public key for secure message exchange
returns:
    privatekey = RSA private key used in decryption of received messages
    publickey = RSA public key that is given for others to encrypt messages with
"""
def generate_keys():
    modulus_length = 256 * 8
    privatekey = RSA.generate(modulus_length, Random.new().read)
    publickey = privatekey.publickey().exportKey(format='PEM', passphrase=None, pkcs=1)
    return privatekey, publickey

def create_encryptionkey():
    return urandom(32)

def encrypt_AES(msg, psw):
    cnt = Counter.new(128)
    if not isinstance(msg, bytes):
        msg = bytes(msg, "utf-8")
    enc = AES.new(psw, AES.MODE_CTR, counter=cnt)
    return enc.encrypt(msg)

def decrypt_AES(msg, psw):
    cnt = Counter.new(128)
    if not isinstance(msg, bytes):
        msg = bytes(msg, "utf-8")
    dec = AES.new(psw, AES.MODE_CTR, counter=cnt)
    return dec.decrypt(msg)
