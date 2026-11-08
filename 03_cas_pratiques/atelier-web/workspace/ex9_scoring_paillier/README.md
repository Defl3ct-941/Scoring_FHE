# Ex9: Score bancaire chiffré de bout en bout

C'est l'exercice de synthèse : vous allez reproduire, avec vos propres
briques (ex6, ex7, ex8), exactement ce que fait la démo web
(`04_demo/backend/app/crypto/paillier.py`, étape "Paillier" de l'interface).

## Le scénario

Un client possède 3 données sensibles (features) : par exemple
`[revenu_centré, ratio_endettement, incidents]`. La banque connaît des
**poids publics** `weights` et un **biais public** `bias`, et veut calculer :

```
score = bias + sum(weight_i * feature_i pour chaque i)
```

... sans jamais voir les `features` en clair.

## À implémenter

- `encrypted_score(pub, priv, features: list[int], weights: list[int], bias: int) -> int`

Étapes à l'intérieur de la fonction :

1. **Côté client** : chiffrer chaque `feature_i` (choisissez un aléa `r`
   différent à chaque fois, par exemple avec `random.randrange`, en
   vérifiant `pgcd(r, n) == 1`).
2. **Côté serveur** : pour chaque `(chiffré, poids)`, calculer
   `mul_by_scalar(pub, chiffré, poids)` puis additionner tous les résultats
   avec `add_encrypted` (le serveur ne voit à aucun moment les valeurs en
   clair !).
3. Ajouter le biais : chiffrez `bias` avec `r = 1` (`encrypt(pub, bias, 1)`)
   puis additionnez-le au total avec `add_encrypted`.
4. **Côté client** : déchiffrer le résultat final et le renvoyer.

## Vérification

Le résultat doit être **rigoureusement identique** au calcul en clair :

```python
plaintext = bias + sum(w * x for w, x in zip(weights, features))
```

C'est exactement la propriété que la démo web démontre à l'étape "Paillier" :
le score est **exact**, calculé sans jamais exposer les données du client.
