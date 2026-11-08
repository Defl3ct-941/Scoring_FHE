# Ex7: Chiffrer et déchiffrer avec Paillier

Avec la paire de clés de l'exercice précédent, vous pouvez maintenant
chiffrer et déchiffrer de vrais nombres.

## Formules

**Chiffrement** d'un message `m` (avec un aléa `r` tel que `pgcd(r, n) = 1`) :

```
c = ((1 + m*n) mod n²) * (r^n mod n²)  mod n²
```

(C'est une simplification équivalente à `g^m * r^n mod n²` quand `g = n+1`,
ce qui évite un `pow` inutilement coûteux.)

**Déchiffrement** :

```
u = c^lam mod n²
L(u) = (u - 1) // n
m = (L(u) * mu) mod n
```

La fonction `L` est déjà fournie dans `exercise.py` (elle est directe, pas
besoin de la réécrire).

## À implémenter

- `encrypt(pub: dict, m: int, r: int) -> int`
- `decrypt(pub: dict, priv: dict, c: int) -> int`

Pour `decrypt`, une subtilité : nos scores peuvent être **négatifs**, alors
que Paillier ne connaît que des nombres entre `0` et `n-1`. On adopte donc
une représentation symétrique : si le résultat déchiffré `m` est supérieur à
`n // 2`, c'est en réalité `m - n` (un nombre négatif). Cette conversion est
à faire à la fin de `decrypt`.

## Indice

Utilisez `pow(base, exp, mod)` ici (le `pow` intégré à 3 arguments est
parfaitement approprié dans ce contexte, vous avez déjà prouvé que vous
compreniez l'algorithme sous-jacent à l'exercice 4 !).
