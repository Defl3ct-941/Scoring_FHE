"""
Ex3 - Chiffrement authentifie avec Fernet.

Voir README.md pour l'enonce complet.
"""

from cryptography.fernet import Fernet, InvalidToken


def encrypt_value(value: str, key: bytes) -> bytes:
    """Chiffre `value` avec Fernet(key)."""
    # TODO: implementez cette fonction
    raise NotImplementedError


def decrypt_value(token: bytes, key: bytes) -> str:
    """Dechiffre `token` avec Fernet(key)."""
    # TODO: implementez cette fonction
    raise NotImplementedError


def tamper_and_check(token: bytes, key: bytes) -> bool:
    """
    Modifie un octet de `token`, tente de le dechiffrer, et renvoie True
    si InvalidToken a bien ete levee (falsification detectee).
    """
    # TODO: implementez cette fonction
    raise NotImplementedError
