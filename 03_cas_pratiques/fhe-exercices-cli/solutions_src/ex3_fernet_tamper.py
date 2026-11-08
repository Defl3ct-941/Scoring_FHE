"""Solution de référence pour ex3_fernet_tamper. Essayez d'abord par vous-même !"""

from cryptography.fernet import Fernet, InvalidToken


def encrypt_value(value: str, key: bytes) -> bytes:
    return Fernet(key).encrypt(value.encode())


def decrypt_value(token: bytes, key: bytes) -> str:
    return Fernet(key).decrypt(token).decode()


def tamper_and_check(token: bytes, key: bytes) -> bool:
    data = bytearray(token)
    data[0] ^= 0xFF
    tampered = bytes(data)
    try:
        Fernet(key).decrypt(tampered)
        return False
    except InvalidToken:
        return True
