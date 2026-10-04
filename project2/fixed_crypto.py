import os
import struct
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key(password, salt):
    # password -> key, slow on purpose
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600_000)
    return kdf.derive(password.encode())


def encrypt_file(in_path, out_path, password):
    salt = os.urandom(16)
    nonce = os.urandom(12)
    with open(in_path, "rb") as f:
        data = f.read()
    # hide real size: length prefix + pad to 1024
    data = struct.pack(">Q", len(data)) + data
    data += b"\x00" * (-len(data) % 1024)
    aad = os.path.basename(out_path).encode()  # tie file to its name
    ciphertext = AESGCM(derive_key(password, salt)).encrypt(nonce, data, aad)
    with open(out_path, "wb") as f:
        f.write(salt + nonce + ciphertext)


def decrypt_file(in_path, out_path, password):
    with open(in_path, "rb") as f:
        blob = f.read()
    salt, nonce, ciphertext = blob[:16], blob[16:28], blob[28:]
    aad = os.path.basename(in_path).encode()
    try:
        data = AESGCM(derive_key(password, salt)).decrypt(nonce, ciphertext, aad)
    except InvalidTag:
        raise SystemExit("decrypt failed: wrong password or file was changed")
    size = struct.unpack(">Q", data[:8])[0]
    with open(out_path, "wb") as f:
        f.write(data[8:8 + size])


if __name__ == "__main__":
    import getpass
    pw = getpass.getpass("Password: ")
    encrypt_file("secret.txt", "secret.enc", pw)
    decrypt_file("secret.enc", "recovered.txt", pw)
    print(open("recovered.txt").read())
