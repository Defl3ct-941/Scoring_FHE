"""Vérifications de ex4_modpow (non distribuées en clair)."""

import random


def test_small_values():
    assert mod_pow(4, 13, 497) == pow(4, 13, 497)
    assert mod_pow(2, 10, 1000) == pow(2, 10, 1000)


def test_exponent_zero():
    assert mod_pow(123, 0, 97) == 1


def test_matches_builtin_pow_on_random_values():
    random.seed(42)
    for _ in range(30):
        base = random.randint(2, 10_000)
        exp = random.randint(0, 1000)
        mod = random.randint(2, 10_000)
        assert mod_pow(base, exp, mod) == pow(base, exp, mod)


def test_large_numbers_like_real_crypto():
    base = 123456789012345678901234567890
    exp = 987654321
    mod = 100000000000000000000000000000000000039
    assert mod_pow(base, exp, mod) == pow(base, exp, mod)
