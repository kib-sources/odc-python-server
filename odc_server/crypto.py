from hashlib import sha256

import rsa


def hash_items(items):
    joined = " ".join([str(i) for i in items])
    joined += "]!L3bP9a@GM6U*LL"
    hex_hash = sha256(joined.encode()).hexdigest()
    return hex_hash


def sign_with_private_key(item, key):
    private_key = rsa.PrivateKey.load_pkcs1(key.encode())
    data = bytes(bytearray.fromhex(item))
    signed_data = rsa.sign(data, private_key, "SHA-256").hex()
    return signed_data
