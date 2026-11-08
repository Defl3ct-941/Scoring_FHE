# Ex5: PGCD étendu et inverse modulaire

Le déchiffrement de Paillier (prochains exercices) a besoin de calculer
l'**inverse modulaire** d'un nombre : trouver `x` tel que
`(a * x) % m == 1`. C'est l'équivalent modulaire de la division.

L'algorithme d'Euclide étendu calcule à la fois le PGCD de deux nombres
**et** les coefficients de Bézout, ce qui donne l'inverse "gratuitement".

## À implémenter

- `extended_gcd(a: int, b: int) -> tuple[int, int, int]` : renvoie
  `(g, x, y)` tel que `a*x + b*y == g`, où `g = pgcd(a, b)`.
- `mod_inverse(a: int, mod: int) -> int` : renvoie `x` tel que
  `(a * x) % mod == 1`, en utilisant `extended_gcd`. Si `a` et `mod` ne sont
  pas premiers entre eux (pgcd ≠ 1), l'inverse n'existe pas : levez une
  `ValueError`.

## Indice : récursion d'Euclide étendu

```
extended_gcd(a, 0) = (a, 1, 0)
extended_gcd(a, b) = (g, y1, x1 - (a // b) * y1)
                      où (g, x1, y1) = extended_gcd(b, a % b)
```

Une fois `(g, x, y)` obtenu pour `extended_gcd(a, mod)`, l'inverse de `a`
modulo `mod` est `x % mod` (pour ramener un éventuel résultat négatif dans
`[0, mod)`).

## Vérification

Vos résultats doivent correspondre à ceux de `pow(a, -1, mod)` (disponible
depuis Python 3.8), qui fait exactement ce calcul en interne.
