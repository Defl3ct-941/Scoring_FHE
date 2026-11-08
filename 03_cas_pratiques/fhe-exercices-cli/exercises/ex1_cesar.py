"""
Ex1 : Le chiffrement de Cesar
=============================

Avant de parler de chiffrement homomorphe, il faut etre a l'aise avec
l'arithmetique modulaire : c'est elle qui est derriere absolument tous les
schemas de chiffrement que vous verrez dans ce projet (Paillier, CKKS...).

Le chiffrement de Cesar decale chaque lettre de `shift` positions dans
l'alphabet, en bouclant a la fin (Z + 1 = A). C'est exactement une addition
modulo 26.

A implementer :
    - caesar_encrypt(text: str, shift: int) -> str
    - caesar_decrypt(text: str, shift: int) -> str

Regles :
    - Les lettres minuscules et majuscules sont decalees, chacune restant
      dans sa casse ('a'..'z' / 'A'..'Z').
    - Tout ce qui n'est pas une lettre (espaces, ponctuation, chiffres,
      accents) est recopie SANS modification.
    - `shift` peut etre negatif ou plus grand que 26 : ca doit fonctionner
      quand meme (pensez a l'operateur %).

Exemple :
    caesar_encrypt("Hello, World!", 3) == "Khoor, Zruog!"
    caesar_decrypt("Khoor, Zruog!", 3) == "Hello, World!"

Indice : pour une lettre `c`, sa position dans l'alphabet est
`ord(c) - ord('a')` (ou ord('A') pour les majuscules), et la nouvelle
position est `(position + shift) % 26`.

ATTENTION : pour detecter si `c` est une lettre, preferez une comparaison
explicite ('a' <= c <= 'z') plutot que c.islower() / c.isupper() : ces
methodes renvoient aussi True pour des lettres accentuees comme e ou a, qui
doivent pourtant rester inchangees.

Testez avec : fhecli run ex1_cesar
"""

# I AM NOT DONE


def caesar_encrypt(text: str, shift: int) -> str:
    """Decale chaque lettre de `text` de `shift` positions (modulo 26)."""
    # TODO: implementez cette fonction
    raise NotImplementedError


def caesar_decrypt(text: str, shift: int) -> str:
    """Operation inverse de caesar_encrypt."""
    # TODO: implementez cette fonction
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests : ne modifiez pas cette section, elle valide votre implementation.
# ---------------------------------------------------------------------------


def test_known_vector():
    assert caesar_encrypt("Hello, World!", 3) == "Khoor, Zruog!"


def test_decrypt_is_inverse_of_encrypt():
    for shift in [1, 3, 13, 25]:
        for text in ["Bonjour", "PYTHON is FUN", "a b c Z"]:
            enc = caesar_encrypt(text, shift)
            assert caesar_decrypt(enc, shift) == text


def test_non_letters_untouched():
    assert caesar_encrypt("123 !? éà", 5) == "123 !? éà"


def test_wraps_around_alphabet():
    assert caesar_encrypt("xyz", 3) == "abc"
    assert caesar_encrypt("XYZ", 3) == "ABC"


def test_negative_and_large_shift():
    assert caesar_encrypt("abc", -1) == caesar_encrypt("abc", 25)
    assert caesar_encrypt("abc", 29) == caesar_encrypt("abc", 3)


def test_case_is_preserved():
    result = caesar_encrypt("AbC", 1)
    assert result[0].isupper() and result[1].islower() and result[2].isupper()


def test_accented_letters_are_not_shifted():
    assert caesar_encrypt("café", 1) == "dbgé"
