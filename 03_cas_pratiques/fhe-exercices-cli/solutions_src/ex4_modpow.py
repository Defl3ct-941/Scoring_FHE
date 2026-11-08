"""Solution de référence pour ex4_modpow. Essayez d'abord par vous-même !"""


def mod_pow(base: int, exp: int, mod: int) -> int:
    result = 1
    base = base % mod
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp //= 2
    return result
