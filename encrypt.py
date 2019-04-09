from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random
from Crypto.PublicKey import RSA


"""
Encrypts the message for the client with the given publickey
msg = message to be encrypted
publickey = publickey used in encryption as received from generate_keys
return bytes
"""
def encrypt(msg, publickey):
    if type(msg) == str:
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
def decrypt(msg, privatekey):
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
    modulus_length = 256 * 16
    privatekey = RSA.generate(modulus_length, Random.new().read)
    publickey = privatekey.publickey().exportKey(format='PEM', passphrase=None, pkcs=1)
    return privatekey, publickey

def create_encryptionkey():
    return "secret_password"

