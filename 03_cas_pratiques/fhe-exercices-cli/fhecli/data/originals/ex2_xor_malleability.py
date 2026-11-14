"""
Ex2 : XOR et le danger de la malléabilité
==========================================

Le XOR (^) a une propriété étonnante : si `k` est une clé et `m` un message
(en octets), alors :

    chiffrer(m, k)   = m XOR k
    déchiffrer(c, k) = c XOR k    (car (m XOR k) XOR k == m)

C'est un chiffrement « homomorphe » jouet... mais c'est justement ce qui le
rend dangereux dès qu'on réutilise la même clé deux fois : c'est l'attaque
classique du « two-time pad ».

À implémenter :
    - xor_bytes(a: bytes, b: bytes) -> bytes
      XOR octet par octet de deux suites de même longueur.
    - xor_encrypt(message: bytes, key: bytes) -> bytes
      XOR du message avec la clé répétée autant de fois que nécessaire pour
      couvrir sa longueur. (xor_decrypt est déjà fourni : le XOR est son
      propre inverse.)
    - reveal_xor_of_plaintexts(c1: bytes, c2: bytes) -> bytes
      Si c1 et c2 sont deux messages chiffrés AVEC LA MÊME clé, cette
      fonction doit renvoyer le XOR des deux messages en clair, SANS jamais
      connaître la clé. (Indice : une seule ligne, qui réutilise xor_bytes.)

Pourquoi c'est important : ceci illustre une idée centrale du projet. Dans
un chiffrement classique, toute malléabilité est une faille de sécurité.
Ici, réutiliser la clé permet de retrouver de l'information sur les
messages en clair sans jamais les déchiffrer. Le FHE renverse ce principe :
il rend le chiffré délibérément et strictement malléable, mais uniquement
pour les opérations mathématiques choisies par le concepteur du schéma
(addition, multiplication...), avec une sécurité ramenée à des problèmes
mathématiques réputés difficiles.
C'est toute la différence entre une malléabilité subie (dangereuse) et une
malléabilité conçue (le FHE).

Vérifiez avec : fhe-cli check ex2
"""

# I AM NOT DONE


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR octet par octet. `a` et `b` ont la même longueur."""
    # TODO: implémentez cette fonction
    raise NotImplementedError


def xor_encrypt(message: bytes, key: bytes) -> bytes:
    """Chiffre `message` en le XORant avec `key` répétée."""
    # TODO: implémentez cette fonction (réutilisez xor_bytes)
    raise NotImplementedError


def xor_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """Le XOR est son propre inverse : déchiffrer = chiffrer à nouveau."""
    return xor_encrypt(ciphertext, key)


def reveal_xor_of_plaintexts(c1: bytes, c2: bytes) -> bytes:
    """
    Si c1 et c2 ont été chiffrés avec LA MÊME clé (two-time pad), renvoie
    le XOR des deux messages en clair, sans jamais connaître la clé.
    """
    # TODO: implémentez cette fonction
    raise NotImplementedError
