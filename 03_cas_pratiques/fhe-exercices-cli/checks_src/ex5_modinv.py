"""Vérifications de ex5_modinv (non distribuées en clair)."""

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
