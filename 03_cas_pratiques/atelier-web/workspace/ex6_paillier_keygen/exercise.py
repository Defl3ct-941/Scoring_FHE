"""
Ex6 - Generer une paire de cles Paillier.

Voir README.md pour l'enonce complet.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ex5_modinv.exercise import mod_inverse  # reutilise votre travail de l'ex5


def generate_keypair(p: int, q: int) -> tuple[dict, dict]:
    """
    Construit une paire de cles Paillier simplifiee (g = n + 1).

    Retourne (public_key, private_key) avec :
      public_key  = {"n": n, "g": g, "n2": n * n}
      private_key = {"lam": lam, "mu": mu}
    """
    # TODO: implementez cette fonction (formules dans le README)
    raise NotImplementedError
