import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from backend.core.config import get_settings


NONCE_SIZE = 12


def encrypt_bytes(plaintext: bytes) -> bytes:
    key = get_settings().encryption_key
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce + ciphertext


def decrypt_bytes(blob: bytes) -> bytes:
    if len(blob) <= NONCE_SIZE:
        raise ValueError("Encrypted blob is invalid.")
    key = get_settings().encryption_key
    aesgcm = AESGCM(key)
    nonce = blob[:NONCE_SIZE]
    ciphertext = blob[NONCE_SIZE:]
    return aesgcm.decrypt(nonce, ciphertext, None)
