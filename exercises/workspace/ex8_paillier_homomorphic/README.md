# Ex8: Propriétés homomorphes de Paillier

Voici enfin la magie : deux opérations qu'on peut faire **directement sur
les chiffrés**, sans jamais les déchiffrer.

## Formules

**Addition chiffrée** (le produit de deux chiffrés donne le chiffré de la
somme) :

```
E(a) * E(b) mod n²  =  E(a + b mod n)
```

**Multiplication par un scalaire clair** (élever un chiffré à la puissance
`k` donne le chiffré de `k` fois le message) :

```
E(a) ^ k mod n²  =  E(k * a mod n)
```

## À implémenter

- `add_encrypted(pub: dict, c1: int, c2: int) -> int`
- `mul_by_scalar(pub: dict, c: int, k: int) -> int`

`k` peut être **négatif** (poids négatif dans un score, par exemple). Dans
ce cas, `E(a)^k` n'a pas de sens directement en Python (exposant négatif
avec `pow(..., mod)` lève une erreur sauf cas particulier) : il faut plutôt
calculer l'**inverse modulaire** du chiffré, puis l'élever à la puissance
`-k` (qui est positive) :

```
E(a) ^ (-k) mod n²   ==   inverse_modulaire(E(a), n²) ^ k  mod n²
```

Vous pouvez utiliser `pow(x, -1, mod)` directement pour l'inverse modulaire
ici (Python le supporte nativement depuis la 3.8), ou réutiliser votre
`mod_inverse` de l'ex5.

## Vérification attendue

```python
pub, priv = generate_keypair(1009, 1013)
c3 = encrypt(pub, 3, r1)
c5 = encrypt(pub, 5, r2)
decrypt(pub, priv, add_encrypted(pub, c3, c5)) == 8

c4 = encrypt(pub, 4, r3)
decrypt(pub, priv, mul_by_scalar(pub, c4, 3)) == 12
decrypt(pub, priv, mul_by_scalar(pub, c4, -2)) == -8
```
