"""
Ex4 : Exponentiation modulaire rapide (square-and-multiply)
============================================================

On quitte le chiffrement classique pour poser les briques mathématiques du
chiffrement homomorphe. La toute première est l'exponentiation modulaire :
calculer (base ** exp) % mod. Paillier, RSA et beaucoup d'autres schémas
reposent dessus, avec des exposants de plusieurs centaines de chiffres.

Calculer base ** exp puis prendre le modulo est impossible en pratique : le
nombre intermédiaire aurait des millions de chiffres. L'algorithme
« square-and-multiply » garde au contraire des nombres petits (toujours
réduits modulo `mod`) en parcourant l'exposant bit par bit.

À implémenter :
    - mod_pow(base, exp, mod) -> int
      Calcule (base ** exp) % mod SANS passer par base ** exp.

Algorithme :
    result = 1
    base = base % mod
    tant que exp > 0 :
        si le bit de poids faible de exp vaut 1 (exp & 1) :
            result = (result * base) % mod
        base = (base * base) % mod   # on élève base au carré
        exp = exp // 2               # on passe au bit suivant

Contrainte : n'utilisez pas le pow(base, exp, mod) intégré à trois arguments
(c'est justement ce que vous reconstruisez ici). Vous pourrez l'utiliser dans
les exercices suivants.

Testez avec : fhe-cli run ex4_modpow
"""

# I AM NOT DONE


def mod_pow(base: int, exp: int, mod: int) -> int:
    """Calcule (base ** exp) % mod par exponentiation rapide."""
    # TODO: implémentez l'algorithme square-and-multiply décrit ci-dessus
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests : ne modifiez pas cette section, elle valide votre implémentation.
# ---------------------------------------------------------------------------

import random


def test_small_values():
    assert mod_pow(4, 13, 497) == pow(4, 13, 497)
    assert mod_pow(2, 10, 1000) == pow(2, 10, 1000)


def test_exponent_zero():
    assert mod_pow(123, 0, 97) == 1


def test_matches_builtin_pow_on_random_values():
    random.seed(42)
    for _ in range(30):
        base = random.randint(2, 10_000)
        exp = random.randint(0, 1000)
        mod = random.randint(2, 10_000)
        assert mod_pow(base, exp, mod) == pow(base, exp, mod)


def test_large_numbers_like_real_crypto():
    base = 123456789012345678901234567890
    exp = 987654321
    mod = 100000000000000000000000000000000000039
    assert mod_pow(base, exp, mod) == pow(base, exp, mod)
