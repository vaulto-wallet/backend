from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256


def sing_object(data, fields, private_key):
    bytesdata = bytes()
    for f in fields.sort():
        bytesdata+=data[f].encode()
    return bytesdata





