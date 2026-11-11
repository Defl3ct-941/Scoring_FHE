"""
Ex6 : Générer une paire de clés Paillier
==========================================

On attaque le chiffrement homomorphe partiel de Paillier (1999). Sa propriété
remarquable : on peut ADDITIONNER deux messages chiffrés sans les déchiffrer.
C'est exactement ce qu'il faut pour un score = somme pondérée de features.

Tout commence par les clés. On part de deux nombres premiers p et q (petits
ici, pour que les tests soient rapides ; énormes en vrai).

Les deux fonctions utilitaires _extended_gcd et _mod_inverse sont déjà
fournies (c'est votre travail de l'ex5). Vous n'implémentez que la génération
de clés.

À implémenter :
    - generate_keypair(p, q) -> (public_key, private_key)
      avec la variante classique g = n + 1 :
          n   = p * q
          g   = n + 1
          lam = (p - 1) * (q - 1)          # lambda = indicatrice d'Euler
          mu  = inverse modulaire de lam modulo n
      puis :
          public_key  = {"n": n, "g": g, "n2": n * n}
          private_key = {"lam": lam, "mu": mu}

Vérifiez avec : fhe-cli check ex6
"""

# I AM NOT DONE


def _extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    """Fourni (ex5) : (g, x, y) tel que a*x + b*y == g == pgcd(a, b)."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = _extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def _mod_inverse(a: int, mod: int) -> int:
    """Fourni (ex5) : inverse modulaire de a modulo mod."""
    g, x, _ = _extended_gcd(a, mod)
    if g != 1:
        raise ValueError(f"{a} n'a pas d'inverse modulo {mod}")
    return x % mod


def generate_keypair(p: int, q: int) -> tuple[dict, dict]:
    """Construit une paire de clés Paillier simplifiée (g = n + 1)."""
    # TODO: calculez n, g, lam, mu et renvoyez (public_key, private_key)
    raise NotImplementedError
