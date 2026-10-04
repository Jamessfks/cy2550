import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_file(in_path: str, out_path: str, key: bytes) -> None:
    nonce = os.urandom(12)                      # unique per encryption
    with open(in_path, "rb") as f:
        ciphertext = AESGCM(key).encrypt(nonce, f.read(), None)
    with open(out_path, "wb") as f:
        f.write(nonce + ciphertext)             # store nonce up front
