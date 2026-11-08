"""
Ex8 - Proprietes homomorphes de Paillier (addition, multiplication par scalaire).

Voir README.md pour l'enonce complet.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ex6_paillier_keygen.exercise import generate_keypair  # noqa: F401
from ex7_paillier_enc_dec.exercise import decrypt, encrypt  # noqa: F401


def add_encrypted(pub: dict, c1: int, c2: int) -> int:
    """Renvoie E(a + b) a partir de E(a) = c1 et E(b) = c2."""
    # TODO: implementez cette fonction
    raise NotImplementedError


def mul_by_scalar(pub: dict, c: int, k: int) -> int:
    """Renvoie E(k * a) a partir de E(a) = c et d'un scalaire clair k (peut etre negatif)."""
    # TODO: implementez cette fonction
    raise NotImplementedError
