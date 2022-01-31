from argon2 import PasswordHasher
import argon2
from cryptography.fernet import Fernet
import base64
from config import ENCRYPTION_KEY

ph = PasswordHasher()
key = ENCRYPTION_KEY
f = Fernet(key)

def encrypt(password_plain):
    global ph
    hash = ph.hash(password_plain)
    return hash

def verify_hash(hash_in, plain_text):
    global ph
    try:
        ph.verify(hash_in, plain_text)
    except Exception as e:
        if e == argon2.exceptions.VerifyMismatchError:
            return False
        else:
            return False
    return True

def fernet_encrypt(text):
    global f
    text = str(text)
    plain_text = text.encode()
    cipher_text = f.encrypt(plain_text)
    cipher_text = cipher_text.decode()
    return cipher_text

def fernet_decrypt(text):
    global f
    text = str(text)
    cipher_text = text.encode()
    plain_text = f.decrypt(cipher_text)
    plain_text = plain_text.decode()
    return plain_text
