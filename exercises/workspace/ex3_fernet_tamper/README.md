# Ex3: Chiffrement authentifié avec Fernet

Dans la démo (`demo/backend/app/crypto/classic_aes.py`), on utilise
`Fernet` (AES-128-CBC + HMAC) pour montrer qu'un chiffrement classique
détecte et rejette toute donnée falsifiée. Ici, vous allez reproduire ce
comportement vous-même, avec la vraie bibliothèque `cryptography`.

## À implémenter

- `encrypt_value(value: str, key: bytes) -> bytes` : chiffre une chaîne avec
  `Fernet(key)`. `value` doit être encodée en bytes avant chiffrement
  (`value.encode()`).
- `decrypt_value(token: bytes, key: bytes) -> str` : opération inverse,
  renvoie une chaîne (`.decode()`).
- `tamper_and_check(token: bytes, key: bytes) -> bool` : modifie **un seul
  octet** du token (par exemple en inversant ses bits avec XOR 0xFF), puis
  tente de le déchiffrer. Renvoie `True` si la falsification est détectée
  (exception `cryptography.fernet.InvalidToken` levée), `False` sinon.

## Indice

```python
from cryptography.fernet import Fernet, InvalidToken

key = Fernet.generate_key()   # à utiliser dans les tests, pas dans vos fonctions
```

Pour modifier un octet d'un `bytes` (immuable), passez par une liste :

```python
data = bytearray(token)
data[0] ^= 0xFF
tampered = bytes(data)
```

## Ce que ça démontre

Un chiffrement authentifié ne laisse **aucune marge de manœuvre** : la
moindre modification du chiffré, même un seul bit, est détectée. C'est une
excellente propriété de sécurité... mais c'est aussi précisément ce qui rend
tout calcul sur le chiffré impossible avec ce type de schéma.
