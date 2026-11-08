"""
Ex2 : XOR et le danger de la malleabilite
==========================================

Le XOR (^) a une propriete etonnante : si `k` est une cle et `m` un message
(en octets), alors :

    chiffrer(m, k)   = m XOR k
    dechiffrer(c, k) = c XOR k    (car (m XOR k) XOR k == m)

C'est un chiffrement "homomorphe" jouet... mais c'est justement ce qui le
rend dangereux des qu'on reutilise la meme cle deux fois : c'est l'attaque
classique du "two-time pad".

A implementer :
    - xor_bytes(a: bytes, b: bytes) -> bytes
      XOR octet par octet de deux suites de meme longueur.
    - xor_encrypt(message: bytes, key: bytes) -> bytes
      XOR le message avec la cle repetee autant de fois que necessaire pour
      couvrir sa longueur. (xor_decrypt est deja fourni : le XOR est son
      propre inverse.)
    - reveal_xor_of_plaintexts(c1: bytes, c2: bytes) -> bytes
      Si c1 et c2 sont deux messages chiffres AVEC LA MEME cle, cette
      fonction doit renvoyer le XOR des deux messages en clair, SANS jamais
      connaitre la cle. (Indice : une seule ligne, qui reutilise xor_bytes.)

Pourquoi c'est important : ceci illustre une idee centrale du projet. Dans
un chiffrement classique, toute malleabilite est une faille de securite.
Ici, reutiliser la cle permet de retrouver de l'information sur les
messages en clair sans jamais les dechiffrer. Le FHE renverse ce principe :
il rend le chiffre delibrement et strictement malleable, mais uniquement
pour les operations mathematiques choisies par le concepteur du schema
(addition, multiplication...), avec des garanties de securite prouvees.
C'est toute la difference entre une malleabilite subie (dangereuse) et une
malleabilite concue (le FHE).

Testez avec : fhecli run ex2_xor_malleability
"""

# I AM NOT DONE


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR octet par octet. `a` et `b` ont la meme longueur."""
    # TODO: implementez cette fonction
    raise NotImplementedError


def xor_encrypt(message: bytes, key: bytes) -> bytes:
    """Chiffre `message` en le XORant avec `key` repetee."""
    # TODO: implementez cette fonction (reutilisez xor_bytes)
    raise NotImplementedError


def xor_decrypt(ciphertext: bytes, key: bytes) -> bytes:
    """Le XOR est son propre inverse : dechiffrer = chiffrer a nouveau."""
    return xor_encrypt(ciphertext, key)


def reveal_xor_of_plaintexts(c1: bytes, c2: bytes) -> bytes:
    """
    Si c1 et c2 ont ete chiffres avec LA MEME cle (two-time pad), renvoie
    le XOR des deux messages en clair, sans jamais connaitre la cle.
    """
    # TODO: implementez cette fonction
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests : ne modifiez pas cette section, elle valide votre implementation.
# ---------------------------------------------------------------------------


def test_xor_bytes_basic():
    assert xor_bytes(b"\x00\xff", b"\xff\x00") == b"\xff\xff"
    assert xor_bytes(b"AB", b"AB") == b"\x00\x00"


def test_encrypt_decrypt_roundtrip():
    key = b"secret"
    for message in [b"hello world", b"a", b"", b"x" * 50]:
        enc = xor_encrypt(message, key)
        assert xor_decrypt(enc, key) == message


def test_key_is_repeated():
    key = b"ab"
    message = b"1234"
    enc = xor_encrypt(message, key)
    assert enc == xor_bytes(message, b"abab")


def test_two_time_pad_attack():
    key = b"supersecretkey!!"
    p1 = b"TRANSFER 100 EUR"
    p2 = b"TRANSFER 999 EUR"
    c1 = xor_encrypt(p1, key)
    c2 = xor_encrypt(p2, key)

    # sans connaitre `key`, on doit retrouver p1 XOR p2
    revealed = reveal_xor_of_plaintexts(c1, c2)
    assert revealed == xor_bytes(p1, p2)
