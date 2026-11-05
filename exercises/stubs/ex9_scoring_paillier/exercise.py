"""
Ex9 - Score bancaire chiffre de bout en bout (synthese).

Voir README.md pour l'enonce complet.
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ex6_paillier_keygen.exercise import generate_keypair  # noqa: F401
from ex7_paillier_enc_dec.exercise import decrypt, encrypt  # noqa: F401
from ex8_paillier_homomorphic.exercise import add_encrypted, mul_by_scalar  # noqa: F401


def _random_r(n: int) -> int:
    r = random.randrange(2, n)
    while math.gcd(r, n) != 1:
        r = random.randrange(2, n)
    return r


def encrypted_score(pub: dict, priv: dict, features: list[int], weights: list[int], bias: int) -> int:
    """
    Calcule bias + sum(w_i * feature_i) SANS jamais dechiffrer les features
    individuellement : seul le score final est dechiffre, a la toute fin.
    """
    # TODO: implementez cette fonction (etapes detaillees dans le README)
    raise NotImplementedError
