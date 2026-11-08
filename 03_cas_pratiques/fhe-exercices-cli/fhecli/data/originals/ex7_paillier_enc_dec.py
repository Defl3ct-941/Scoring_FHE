"""
Ex7 : Chiffrer et déchiffrer avec Paillier
============================================

Les clés sont prêtes (ex6, fourni ci-dessous). On chiffre maintenant un entier
m, puis on le retrouve par déchiffrement.

Chiffrement, avec un aléa r tel que pgcd(r, n) == 1 :
    c = (1 + m*n) * (r ** n)   modulo n2
(la variante g = n + 1 permet d'écrire g**m = 1 + m*n modulo n2, bien plus
rapide à calculer). L'aléa r rend deux chiffrés du même message différents.

Déchiffrement, avec la fonction L(u) = (u - 1) // n (fournie) :
    u = (c ** lam)      modulo n2
    m = (L(u) * mu)     modulo n

Représentation symétrique : pour pouvoir manipuler des nombres négatifs (un
score peut être négatif), on convient que les valeurs supérieures à n/2
représentent des négatifs. Donc après déchiffrement, si m > n // 2, faites
m -= n.

À implémenter :
    - encrypt(pub, m, r) -> int
    - decrypt(pub, priv, c) -> int   (avec la correction symétrique ci-dessus)

Vous pouvez utiliser le pow(base, exp, mod) intégré ici.

Testez avec : fhe-cli run ex7_paillier_enc_dec
"""

# I AM NOT DONE


def _extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = _extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def _mod_inverse(a: int, mod: int) -> int:
    g, x, _ = _extended_gcd(a, mod)
    if g != 1:
        raise ValueError(f"{a} n'a pas d'inverse modulo {mod}")
    return x % mod


def generate_keypair(p: int, q: int) -> tuple[dict, dict]:
    """Fourni (ex6)."""
    n = p * q
    g = n + 1
    lam = (p - 1) * (q - 1)
    mu = _mod_inverse(lam, n)
    return {"n": n, "g": g, "n2": n * n}, {"lam": lam, "mu": mu}


def _l(u: int, n: int) -> int:
    """Fonction L(u) = (u - 1) // n, fournie telle quelle."""
    return (u - 1) // n


def encrypt(pub: dict, m: int, r: int) -> int:
    """Chiffre l'entier m avec l'aléa r (pgcd(r, n) == 1)."""
    # TODO: implémentez la formule de chiffrement
    raise NotImplementedError


def decrypt(pub: dict, priv: dict, c: int) -> int:
    """Déchiffre c. Gère la représentation symétrique pour les négatifs."""
    # TODO: implémentez la formule de déchiffrement, puis la correction m > n//2
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests : ne modifiez pas cette section, elle valide votre implémentation.
# ---------------------------------------------------------------------------

import math
import random

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
    assert c1 != c2  # aléatoire -> chiffrés différents...
    assert decrypt(pub, priv, c1) == 7  # ... mais même message une fois déchiffré
    assert decrypt(pub, priv, c2) == 7


def test_negative_number_via_symmetric_representation():
    pub, priv = generate_keypair(P, Q)
    n = pub["n"]
    rng = random.Random(3)
    r = _random_r(n, rng)
    # -5 est représenté comme (n - 5) dans Z_n
    c = encrypt(pub, n - 5, r)
    assert decrypt(pub, priv, c) == -5
