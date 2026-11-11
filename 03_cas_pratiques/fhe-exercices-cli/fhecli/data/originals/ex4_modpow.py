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

Vérifiez avec : fhe-cli check ex4
"""

# I AM NOT DONE


def mod_pow(base: int, exp: int, mod: int) -> int:
    """Calcule (base ** exp) % mod par exponentiation rapide."""
    # TODO: implémentez l'algorithme square-and-multiply décrit ci-dessus
    raise NotImplementedError
