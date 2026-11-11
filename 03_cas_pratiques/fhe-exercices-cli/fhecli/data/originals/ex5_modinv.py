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

Vérifiez avec : fhe-cli check ex5
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
