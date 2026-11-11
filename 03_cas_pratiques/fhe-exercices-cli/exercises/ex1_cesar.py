"""
Ex1 : Le chiffrement de César
=============================

Avant de parler de chiffrement homomorphe, il faut être à l'aise avec
l'arithmétique modulaire : c'est elle qui est derrière absolument tous les
schémas de chiffrement que vous verrez dans ce projet (Paillier, CKKS...).

Le chiffrement de César décale chaque lettre de `shift` positions dans
l'alphabet, en bouclant à la fin (Z + 1 = A). C'est exactement une addition
modulo 26.

À implémenter :
    - caesar_encrypt(text: str, shift: int) -> str
    - caesar_decrypt(text: str, shift: int) -> str

Règles :
    - Les lettres minuscules et majuscules sont décalées, chacune restant
      dans sa casse ('a'..'z' / 'A'..'Z').
    - Tout ce qui n'est pas une lettre (espaces, ponctuation, chiffres,
      lettres accentuées) est recopié SANS modification.
    - `shift` peut être négatif ou plus grand que 26 : ça doit fonctionner
      quand même (pensez à l'opérateur %).

Exemple :
    caesar_encrypt("Hello, World!", 3) == "Khoor, Zruog!"
    caesar_decrypt("Khoor, Zruog!", 3) == "Hello, World!"

Indice : pour une lettre `c`, sa position dans l'alphabet est
`ord(c) - ord('a')` (ou ord('A') pour les majuscules), et la nouvelle
position est `(position + shift) % 26`.

ATTENTION : pour détecter si `c` est une lettre, préférez une comparaison
explicite ('a' <= c <= 'z') plutôt que c.islower() / c.isupper() : ces
méthodes renvoient aussi True pour des lettres accentuées comme « é » ou
« à », qui doivent pourtant rester inchangées.

Vérifiez avec : fhe-cli check ex1
"""

# I AM NOT DONE


def caesar_encrypt(text: str, shift: int) -> str:
    """Décale chaque lettre de `text` de `shift` positions (modulo 26)."""
    # TODO: implémentez cette fonction
    raise NotImplementedError


def caesar_decrypt(text: str, shift: int) -> str:
    """Opération inverse de caesar_encrypt."""
    # TODO: implémentez cette fonction
    raise NotImplementedError
