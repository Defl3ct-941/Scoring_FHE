import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exercise import add_encrypted, decrypt, encrypt, generate_keypair, mul_by_scalar

P, Q = 1009, 1013


def _random_r(n: int, rng: random.Random) -> int:
    r = rng.randrange(2, n)
    while math.gcd(r, n) != 1:
        r = rng.randrange(2, n)
    return r


def test_homomorphic_addition():
    pub, priv = generate_keypair(P, Q)
    rng = random.Random(10)
    c3 = encrypt(pub, 3, _random_r(pub["n"], rng))
    c5 = encrypt(pub, 5, _random_r(pub["n"], rng))
    c_sum = add_encrypted(pub, c3, c5)
    assert decrypt(pub, priv, c_sum) == 8


def test_homomorphic_addition_is_commutative():
    pub, priv = generate_keypair(P, Q)
    rng = random.Random(11)
    c_a = encrypt(pub, 17, _random_r(pub["n"], rng))
    c_b = encrypt(pub, 25, _random_r(pub["n"], rng))
    assert decrypt(pub, priv, add_encrypted(pub, c_a, c_b)) == decrypt(
        pub, priv, add_encrypted(pub, c_b, c_a)
    )


def test_mul_by_positive_scalar():
    pub, priv = generate_keypair(P, Q)
    rng = random.Random(12)
    c4 = encrypt(pub, 4, _random_r(pub["n"], rng))
    assert decrypt(pub, priv, mul_by_scalar(pub, c4, 3)) == 12


def test_mul_by_negative_scalar():
    pub, priv = generate_keypair(P, Q)
    rng = random.Random(13)
    c4 = encrypt(pub, 4, _random_r(pub["n"], rng))
    assert decrypt(pub, priv, mul_by_scalar(pub, c4, -2)) == -8


def test_weighted_sum_like_scoring():
    pub, priv = generate_keypair(P, Q)
    rng = random.Random(14)
    features = [100, 20, 3]
    weights = [2, -5, -10]
    ciphertexts = [encrypt(pub, x, _random_r(pub["n"], rng)) for x in features]
    terms = [mul_by_scalar(pub, c, w) for c, w in zip(ciphertexts, weights)]
    total = terms[0]
    for t in terms[1:]:
        total = add_encrypted(pub, total, t)
    expected = sum(w * x for w, x in zip(weights, features))
    assert decrypt(pub, priv, total) == expected
