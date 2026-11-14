# Ex2: XOR et le danger de la malléabilité

Le `XOR` (`^`) a une propriété étonnante : si `k` est une clé et `m` un
message (en octets), alors :

```
chiffrer(m, k)     = m XOR k
dechiffrer(c, k)   = c XOR k    (car (m XOR k) XOR k == m)
```

C'est un chiffrement "homomorphe" jouet... mais c'est justement ce qui le
rend **dangereux** dès qu'on réutilise la même clé deux fois : c'est
l'attaque classique du "two-time pad".

## À implémenter

- `xor_bytes(a: bytes, b: bytes) -> bytes` : XOR octet par octet de deux
  suites de même longueur.
- `xor_encrypt(message: bytes, key: bytes) -> bytes` : XOR le message avec la
  clé répétée autant de fois que nécessaire pour couvrir sa longueur.
  (`xor_decrypt` est la même opération : le XOR est son propre inverse.)
- `reveal_xor_of_plaintexts(c1: bytes, c2: bytes) -> bytes` : si `c1` et `c2`
  sont deux messages chiffrés **avec la même clé**, cette fonction doit
  renvoyer le XOR des deux messages en clair, **sans jamais connaître la
  clé**. (Indice : c'est une seule ligne, qui réutilise `xor_bytes`.)

## Pourquoi c'est important

Ceci illustre une idée centrale du projet : dans un chiffrement classique,
**toute malléabilité est une faille de sécurité**. Ici, réutiliser la clé
permet de retrouver de l'information sur les messages en clair sans jamais
les déchiffrer. Le FHE renverse ce principe : il rend le chiffré
**délibérément et strictement malléable**, mais uniquement pour les
opérations mathématiques choisies par le concepteur du schéma (addition,
multiplication...), avec une sécurité ramenée à des problèmes mathématiques
réputés difficiles. C'est toute la
différence entre une malléabilité *subie* (dangereuse) et une malléabilité
*conçue* (le FHE).
