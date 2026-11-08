"""
Ex5 : PGCD étendu et inverse modulaire
=======================================

Deuxième brique mathématique. Dans Paillier, le déchiffrement a besoin de
« diviser » modulo n, c'est-à-dire de multiplier par un inverse modulaire :
l'entier x tel que (a * x) % mod == 1. Cet inverse n'existe que si a et mod
sont premiers entre eux (pgcd == 1).

On l'obtient avec l'algorithme d'Euclide étendu, qui calcule en même temps le
pgcd de a et b et les coefficients de Bézout x, y tels que a*x + b*y == pgcd.

À implémenter :
    - extended_gcd(a, b) -> (g, x, y)
      avec a*x + b*y == g == pgcd(a, b). Version récursive :
          si b == 0 : renvoyer (a, 1, 0)
          sinon :
              g, x1, y1 = extended_gcd(b, a % b)
              renvoyer (g, y1, x1 - (a // b) * y1)
    - mod_inverse(a, mod) -> int
      Réutilise extended_gcd. Si g != 1, l'inverse n'existe pas : levez une
      ValueError. Sinon, renvoyez x % mod (le % ramène l'inverse dans
      [0, mod) même si x est négatif).

Testez avec : fhe-cli run ex5_modinv
"""

# I AM NOT DONE


def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Renvoie (g, x, y) tel que a*x + b*y == g == pgcd(a, b)."""
    # TODO: implémentez la récursion décrite ci-dessus
    raise NotImplementedError


def mod_inverse(a: int, mod: int) -> int:
    """Renvoie x tel que (a * x) % mod == 1. Lève ValueError si impossible."""
    # TODO: réutilisez extended_gcd pour calculer l'inverse
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests : ne modifiez pas cette section, elle valide votre implémentation.
# ---------------------------------------------------------------------------

import math
import random

import pytest


def test_extended_gcd_bezout_identity():
    for a, b in [(35, 15), (240, 46), (17, 5), (1000000007, 998244353)]:
        g, x, y = extended_gcd(a, b)
        assert a * x + b * y == g
        assert g == math.gcd(a, b)


def test_mod_inverse_matches_builtin():
    random.seed(7)
    mod = 1_000_000_007  # nombre premier
    for _ in range(20):
        a = random.randint(1, mod - 1)
        assert mod_inverse(a, mod) % mod == pow(a, -1, mod)


def test_mod_inverse_paillier_like_modulus():
    n = 1009 * 1013
    for a in [5, 123, 99999]:
        inv = mod_inverse(a, n)
        assert (a * inv) % n == 1


def test_mod_inverse_raises_when_not_coprime():
    with pytest.raises(ValueError):
        mod_inverse(6, 9)  # pgcd(6, 9) == 3, pas d'inverse
