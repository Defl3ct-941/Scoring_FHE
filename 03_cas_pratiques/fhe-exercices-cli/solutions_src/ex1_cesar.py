"""Solution de référence pour ex1_cesar. Essayez d'abord par vous-même !"""


def _shift_char(c: str, shift: int) -> str:
    if "a" <= c <= "z":
        base = ord("a")
    elif "A" <= c <= "Z":
        base = ord("A")
    else:
        return c
    return chr(base + (ord(c) - base + shift) % 26)


def caesar_encrypt(text: str, shift: int) -> str:
    return "".join(_shift_char(c, shift) for c in text)


def caesar_decrypt(text: str, shift: int) -> str:
    return caesar_encrypt(text, -shift)
