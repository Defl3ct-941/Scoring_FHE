# Ex1: Le chiffrement de César

Avant de parler de chiffrement homomorphe, il faut être à l'aise avec
l'**arithmétique modulaire** : c'est elle qui est derrière absolument tous
les schémas de chiffrement que vous verrez dans ce projet (Paillier, CKKS...).

Le chiffrement de César décale chaque lettre de `shift` positions dans
l'alphabet, en "bouclant" à la fin (Z + 1 = A). C'est exactement une addition
**modulo 26**.

## À implémenter

- `caesar_encrypt(text: str, shift: int) -> str`
- `caesar_decrypt(text: str, shift: int) -> str`

Règles :
- Les lettres minuscules et majuscules sont décalées, chacune restant dans sa
  casse (`a`..`z` / `A`..`Z`).
- Tout ce qui n'est pas une lettre (espaces, ponctuation, chiffres, accents)
  est recopié **sans modification**.
- `shift` peut être négatif ou plus grand que 26 : il faut que ça fonctionne
  quand même (pensez à l'opérateur `%`).

## Exemple

```python
caesar_encrypt("Hello, World!", 3) == "Khoor, Zruog!"
caesar_decrypt("Khoor, Zruog!", 3) == "Hello, World!"
```

## Indice

Pour une lettre `c`, sa position dans l'alphabet est `ord(c) - ord('a')`
(ou `ord('A')` pour les majuscules). Le décalage devient alors :

```
nouvelle_position = (position + shift) % 26
```

⚠️ Pour détecter si `c` est une lettre, préférez une comparaison explicite
(`'a' <= c <= 'z'`) plutôt que `c.islower()` / `c.isupper()` : ces méthodes
renvoient aussi `True` pour des lettres accentuées comme `é` ou `à`, qui
doivent pourtant rester inchangées.
