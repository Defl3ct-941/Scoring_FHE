"""
Ex3 : Chiffrement authentifie avec Fernet
===========================================

Dans la demo web (04_demo/backend/app/crypto/classic_aes.py), on utilise
Fernet (AES-128-CBC + HMAC) pour montrer qu'un chiffrement classique
detecte et rejette toute donnee falsifiee. Ici, vous allez reproduire ce
comportement vous-meme, avec la vraie bibliotheque `cryptography`.

A implementer :
    - encrypt_value(value: str, key: bytes) -> bytes
      Chiffre une chaine avec Fernet(key). `value` doit etre encodee en
      bytes avant chiffrement (value.encode()).
    - decrypt_value(token: bytes, key: bytes) -> str
      Operation inverse, renvoie une chaine (.decode()).
    - tamper_and_check(token: bytes, key: bytes) -> bool
      Modifie UN SEUL octet du token (par exemple en inversant ses bits
      avec XOR 0xFF), puis tente de le dechiffrer. Renvoie True si la
      falsification est detectee (exception InvalidToken levee), False
      sinon.

Indice :
    from cryptography.fernet import Fernet, InvalidToken
    key = Fernet.generate_key()   # a utiliser dans vos propres tests

Pour modifier un octet d'un bytes (immuable), passez par une liste :
    data = bytearray(token)
    data[0] ^= 0xFF
    tampered = bytes(data)

Ce que ca demontre : un chiffrement authentifie ne laisse aucune marge de
manoeuvre. La moindre modification du chiffre, meme un seul bit, est
detectee. C'est une excellente propriete de securite... mais c'est aussi
precisement ce qui rend tout calcul sur le chiffre impossible avec ce type
de schema.

Testez avec : fhecli run ex3_fernet_tamper
"""

from cryptography.fernet import Fernet, InvalidToken

# I AM NOT DONE


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


# ---------------------------------------------------------------------------
# Tests : ne modifiez pas cette section, elle valide votre implementation.
# ---------------------------------------------------------------------------

import pytest


def test_roundtrip():
    key = Fernet.generate_key()
    token = encrypt_value("hello bank", key)
    assert isinstance(token, bytes)
    assert decrypt_value(token, key) == "hello bank"


def test_different_keys_cannot_decrypt():
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    token = encrypt_value("secret data", key1)
    with pytest.raises(Exception):
        decrypt_value(token, key2)


def test_tampering_is_detected():
    key = Fernet.generate_key()
    token = encrypt_value("revenu=4000", key)
    assert tamper_and_check(token, key) is True
