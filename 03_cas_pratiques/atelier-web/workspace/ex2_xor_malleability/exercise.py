"""
Ex2 - XOR et le danger de la malleabilite.

Voir README.md pour l'enonce complet.
"""


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR octet par octet. `a` et `b` ont la meme longueur."""
    # TODO: implementez cette fonction
    raise NotImplementedError


def xor_encrypt(message: bytes, key: bytes) -> bytes:
    """Chiffre `message` en le XORant avec `key` repetee."""
    # TODO: implementez cette fonction (reutilisez xor_bytes)
    raise NotImplementedError


def xor_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """Le XOR est son propre inverse : dechiffrer = chiffrer a nouveau."""
    return xor_encrypt(ciphertext, key)


def reveal_xor_of_plaintexts(c1: bytes, c2: bytes) -> bytes:
    """
    Si c1 et c2 ont ete chiffres avec LA MEME cle (two-time pad), renvoie
    le XOR des deux messages en clair, sans jamais connaitre la cle.
    """
    # TODO: implementez cette fonction
    raise NotImplementedError
