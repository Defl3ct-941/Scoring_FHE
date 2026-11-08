# Ex10 (Bonus): Votre premier calcul FHE avec CKKS

Vous avez construit Paillier vous-même : vous savez maintenant à quel point
c'est déjà un exploit d'implémenter une seule opération homomorphe "à la
main". Implémenter CKKS (le schéma FHE complet utilisé par la démo à
l'étape 3) à la main serait un travail de plusieurs mois. C'est pour ça
qu'on utilise une bibliothèque : **TenSEAL** (qui encapsule Microsoft SEAL).

Cet exercice est volontairement court : le but est d'apprendre à
**utiliser** une bibliothèque FHE réelle, pas à la réimplémenter.

## Fourni (ne pas modifier)

La fonction `make_context()` crée un contexte CKKS déjà paramétré (mêmes
paramètres que la démo). Vous n'avez pas à comprendre chaque paramètre en
détail pour cet exercice, c'est le sujet de l'étape 3 de la démo web.

## À implémenter

- `encrypted_dot_product(context, values: list[float], weights: list[float]) -> float`

Trois lignes suffisent :

1. Chiffrer `values` en un vecteur CKKS : `ts.ckks_vector(context, values)`.
2. Calculer le produit scalaire chiffré avec les poids **en clair** :
   `enc_vector.dot(weights)` (cette opération combine multiplications et
   additions homomorphes, en une seule ligne).
3. Déchiffrer et renvoyer le premier élément du résultat :
   `.decrypt()[0]`.

## À savoir

- Le résultat sera **approximatif** (à `1e-3` près typiquement) : c'est
  normal, CKKS travaille sur des réels avec du bruit numérique, exactement
  comme observé dans la démo.
- ⚠️ TenSEAL ne fournit pas de roue précompilée pour Windows nu : si vous
  n'êtes pas sous Docker/Linux/macOS, cet exercice ne pourra pas s'exécuter
  localement (mais fonctionnera dans l'environnement Docker fourni).
