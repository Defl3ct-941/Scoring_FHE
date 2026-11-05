# Ex4: Exponentiation modulaire rapide

Tous les schémas de chiffrement à clé publique (RSA, Paillier...) reposent
sur le calcul de `base^exp mod m`, avec des exposants qui peuvent avoir
plusieurs centaines de chiffres. Calculer `base ** exp` puis appliquer `% m`
serait bien trop lent (le nombre intermédiaire serait gigantesque).

L'algorithme **"exponentiation rapide" (square-and-multiply)** résout ça en
ne manipulant que des nombres déjà réduits modulo `m`, et en exploitant
l'écriture binaire de l'exposant.

## Principe

```
resultat = 1
base = base % m
tant que exp > 0:
    si exp est impair:
        resultat = (resultat * base) % m
    base = (base * base) % m
    exp = exp // 2
```

## À implémenter

- `mod_pow(base: int, exp: int, mod: int) -> int`

**Contrainte** : vous n'avez le droit d'utiliser que `*`, `%`, `//` et des
boucles, pas le `pow(base, exp, mod)` intégré de Python (le but est de
comprendre l'algorithme qui se cache derrière). Les tests le vérifient en
comparant votre résultat à celui de `pow()`, mais votre implémentation doit
être écrite "à la main".

## Cas particuliers à gérer

- `exp == 0` → doit renvoyer `1 % mod`.
- Fonctionne aussi pour de grands nombres (des dizaines de chiffres).
