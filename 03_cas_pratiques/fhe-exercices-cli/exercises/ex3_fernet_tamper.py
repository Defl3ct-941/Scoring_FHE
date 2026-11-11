"""
Ex3 : Chiffrement authentifié avec Fernet
===========================================

Dans la démo web du projet Scoring FHE (04_demo/backend/app/crypto/classic_aes.py),
on utilise Fernet (AES-128-CBC + HMAC) pour montrer qu'un chiffrement
classique détecte et rejette toute donnée falsifiée. Ici, vous allez
reproduire ce comportement vous-même, avec la vraie bibliothèque
`cryptography`.

À implémenter :
    - encrypt_value(value: str, key: bytes) -> bytes
      Chiffre une chaîne avec Fernet(key). `value` doit être encodée en
      bytes avant chiffrement (value.encode()).
    - decrypt_value(token: bytes, key: bytes) -> str
      Opération inverse, renvoie une chaîne (.decode()).
    - tamper_and_check(token: bytes, key: bytes) -> bool
      Modifie UN SEUL octet du token (par exemple en inversant ses bits
      avec XOR 0xFF), puis tente de le déchiffrer. Renvoie True si la
      falsification est détectée (exception InvalidToken levée), False
      sinon.

Indice :
    from cryptography.fernet import Fernet, InvalidToken
    key = Fernet.generate_key()   # à utiliser dans vos propres tests

Pour modifier un octet d'un objet bytes (immuable), passez par un bytearray :
    data = bytearray(token)
    data[0] ^= 0xFF
    tampered = bytes(data)

Ce que ça démontre : un chiffrement authentifié ne laisse aucune marge de
manœuvre. La moindre modification du chiffré, même d'un seul bit, est
détectée. C'est une excellente propriété de sécurité... mais c'est aussi
précisément ce qui rend tout calcul sur le chiffré impossible avec ce type
de schéma.

Vérifiez avec : fhe-cli check ex3
"""

from cryptography.fernet import Fernet, InvalidToken

# I AM NOT DONE


def encrypt_value(value: str, key: bytes) -> bytes:
    """Chiffre `value` avec Fernet(key)."""
    # TODO: implémentez cette fonction
    raise NotImplementedError


def decrypt_value(token: bytes, key: bytes) -> str:
    """Déchiffre `token` avec Fernet(key)."""
    # TODO: implémentez cette fonction
    raise NotImplementedError


def tamper_and_check(token: bytes, key: bytes) -> bool:
    """
    Modifie un octet de `token`, tente de le déchiffrer, et renvoie True
    si InvalidToken a bien été levée (falsification détectée).
    """
    # TODO: implémentez cette fonction
    raise NotImplementedError
