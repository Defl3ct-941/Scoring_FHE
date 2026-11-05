def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = extended_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse(a: int, mod: int) -> int:
    g, x, _ = extended_gcd(a, mod)
    if g != 1:
        raise ValueError(f"{a} n'a pas d'inverse modulo {mod} (pgcd={g})")
    return x % mod
