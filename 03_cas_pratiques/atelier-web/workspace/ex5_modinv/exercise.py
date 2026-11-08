"""
Ex5 - PGCD etendu et inverse modulaire.

Voir README.md pour l'enonce complet.
"""


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Renvoie (g, x, y) tel que a*x + b*y == g == pgcd(a, b)."""
    # TODO: implementez cette fonction (recursion donnee dans le README)
    raise NotImplementedError


def mod_inverse(a: int, mod: int) -> int:
    """Renvoie x tel que (a * x) % mod == 1. Leve ValueError si impossible."""
    # TODO: implementez cette fonction (reutilisez extended_gcd)
    raise NotImplementedError
