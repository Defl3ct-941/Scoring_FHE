import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exercise import generate_keypair

P, Q = 1009, 1013


def test_public_key_values():
    pub, _ = generate_keypair(P, Q)
    n = P * Q
    assert pub["n"] == n
    assert pub["g"] == n + 1
    assert pub["n2"] == n * n


def test_private_key_values():
    _, priv = generate_keypair(P, Q)
    lam = (P - 1) * (Q - 1)
    n = P * Q
    assert priv["lam"] == lam
    # mu doit etre l'inverse modulaire de lam mod n (verifie independamment)
    assert (priv["mu"] * lam) % n == 1


def test_keys_are_consistent_for_other_primes():
    p, q = 61, 53
    pub, priv = generate_keypair(p, q)
    n = p * q
    lam = (p - 1) * (q - 1)
    assert pub["n"] == n
    assert (priv["mu"] * lam) % n == 1
