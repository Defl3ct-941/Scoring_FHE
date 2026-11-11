"""Vérifications de ex1_cesar (non distribuées en clair)."""

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
