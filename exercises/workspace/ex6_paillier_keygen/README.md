# Ex6: Générer une paire de clés Paillier

C'est le début du chiffrement homomorphe **partiel** utilisé dans la démo
(`demo/backend/app/crypto/paillier.py`) : le schéma de **Paillier** (1999).
Vous allez le reconstruire vous-même, exercice par exercice.

On utilise la variante simplifiée où `g = n + 1` (un choix standard qui
simplifie beaucoup l'implémentation sans rien retirer à la sécurité).

## Rappel des formules

Étant donné deux nombres premiers `p` et `q` :

```
n   = p * q
g   = n + 1
lam = (p - 1) * (q - 1)          (lambda, souvent appelé phi(n) ici)
mu  = inverse_modulaire(lam, n)
```

- La **clé publique** est `(n, g)` (ou juste `n`, puisque `g = n+1`).
- La **clé privée** est `(lam, mu)`.

## À implémenter

- `generate_keypair(p: int, q: int) -> tuple[dict, dict]`

Doit renvoyer `(public_key, private_key)` avec :

```python
public_key  = {"n": n, "g": g, "n2": n * n}
private_key = {"lam": lam, "mu": mu}
```

**Réutilisez la fonction `mod_inverse` que vous avez écrite à l'exercice
précédent** (ex5) pour calculer `mu`, c'est exactement à ça qu'elle sert !
Le fichier `exercise.py` contient déjà l'import qui va bien.

## Pour tester

Les tests utilisent des nombres premiers volontairement petits
(`p = 1009`, `q = 1013`) pour que tout reste rapide et déterministe. En
pratique (et dans la démo `demo/`), on utilise des nombres premiers de
plusieurs centaines de bits.
