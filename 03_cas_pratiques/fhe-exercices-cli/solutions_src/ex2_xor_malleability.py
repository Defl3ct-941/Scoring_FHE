"""Solution de référence pour ex2_xor_malleability. Essayez d'abord par vous-même !"""


def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def xor_encrypt(message: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("key must not be empty")
    repeated_key = (key * (len(message) // len(key) + 1))[: len(message)]
    return xor_bytes(message, repeated_key)


def xor_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    return xor_encrypt(ciphertext, key)


def reveal_xor_of_plaintexts(c1: bytes, c2: bytes) -> bytes:
    return xor_bytes(c1, c2)
