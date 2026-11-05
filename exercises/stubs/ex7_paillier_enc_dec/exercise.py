"""
Ex7 - Chiffrer et dechiffrer avec Paillier.

Voir README.md pour l'enonce complet.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ex6_paillier_keygen.exercise import generate_keypair  # noqa: F401  (reexporte pour les tests)


def _l(u: int, n: int) -> int:
    """Fonction L(u) = (u - 1) // n, fournie telle quelle."""
    return (u - 1) // n


def encrypt(pub: dict, m: int, r: int) -> int:
    """Chiffre l'entier m avec l'alea r (pgcd(r, n) == 1)."""
    # TODO: implementez cette fonction (formule dans le README)
    raise NotImplementedError


def decrypt(pub: dict, priv: dict, c: int) -> int:
    """Dechiffre c. Gere la representation symetrique pour les negatifs."""
    # TODO: implementez cette fonction (formule dans le README)
    raise NotImplementedError
