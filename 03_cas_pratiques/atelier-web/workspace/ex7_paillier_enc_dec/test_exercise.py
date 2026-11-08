import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exercise import decrypt, encrypt, generate_keypair

P, Q = 1009, 1013


def _random_r(n: int, rng: random.Random) -> int:
    r = rng.randrange(2, n)
    while math.gcd(r, n) != 1:
        r = rng.randrange(2, n)
    return r


def test_roundtrip_small_values():
    pub, priv = generate_keypair(P, Q)
    rng = random.Random(1)
    for m in [0, 1, 5, 42, 1000]:
        r = _random_r(pub["n"], rng)
        c = encrypt(pub, m, r)
        assert decrypt(pub, priv, c) == m


def test_different_r_give_different_ciphertexts_same_plaintext():
    pub, priv = generate_keypair(P, Q)
    rng = random.Random(2)
    r1, r2 = _random_r(pub["n"], rng), _random_r(pub["n"], rng)
    c1 = encrypt(pub, 7, r1)
    c2 = encrypt(pub, 7, r2)
    assert c1 != c2  # aleatoire -> chiffres differents...
    assert decrypt(pub, priv, c1) == 7  # ... mais meme message une fois dechiffre
    assert decrypt(pub, priv, c2) == 7


def test_negative_number_via_symmetric_representation():
    pub, priv = generate_keypair(P, Q)
    n = pub["n"]
    rng = random.Random(3)
    r = _random_r(n, rng)
    # -5 est represente comme (n - 5) dans Z_n
    c = encrypt(pub, n - 5, r)
    assert decrypt(pub, priv, c) == -5
