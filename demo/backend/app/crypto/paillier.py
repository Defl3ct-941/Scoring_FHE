"""
ETAPE 2 - Chiffrement homomorphe PARTIEL : Paillier (1999), implemente a la
main pour que chaque etape soit lisible.

Paillier est "partiellement" homomorphe : on peut faire des ADDITIONS sur
les chiffres, et des MULTIPLICATIONS PAR UN NOMBRE EN CLAIR, mais jamais
multiplier deux chiffres entre eux. C'est deja suffisant pour un score
lineaire pondere S = somme(w_i * x_i) car les poids w_i sont publics :

    E(x)^w mod n^2      = E(w * x mod n)      (mult. par un scalaire clair)
    E(x1) * E(x2) mod n^2 = E(x1 + x2 mod n)  (addition)

Variante utilisee : g = n + 1 (cas standard qui simplifie l'implementation
sans rien retirer a la propriete homomorphe).

ATTENTION pedagogique : les tailles de cles sont reduites (512 bits) pour
que la demo reste instantanee dans un navigateur. Des cles Paillier reelles
utilisent generalement 2048+ bits.
"""

import random
import time

from Crypto.Util import number

KEY_BITS = 512
SCALE = 1000  # on travaille sur des entiers (milliemes de point) puis on redivise


def _l(u: int, n: int) -> int:
    return (u - 1) // n


def _modinv(a: int, m: int) -> int:
    return pow(a, -1, m)


def generate_keypair(bits: int = KEY_BITS):
    p = number.getPrime(bits // 2)
    q = number.getPrime(bits // 2)
    while p == q:
        q = number.getPrime(bits // 2)
    n = p * q
    n2 = n * n
    g = n + 1
    lam = (p - 1) * (q - 1)
    mu = _modinv(lam, n)
    public_key = {"n": n, "g": g, "n2": n2}
    private_key = {"lam": lam, "mu": mu}
    return public_key, private_key


def encrypt(pub: dict, m: int) -> int:
    n, n2 = pub["n"], pub["n2"]
    m = m % n
    r = random.randrange(1, n)
    while number.GCD(r, n) != 1:
        r = random.randrange(1, n)
    # (1+n)^m mod n^2 == 1 + m*n mod n^2  -> evite un gros pow(g, m, n2)
    c = ((1 + m * n) % n2) * pow(r, n, n2) % n2
    return c


def decrypt(pub: dict, priv: dict, c: int) -> int:
    n, n2 = pub["n"], pub["n2"]
    u = pow(c, priv["lam"], n2)
    m = (_l(u, n) * priv["mu"]) % n
    # les scores peuvent etre negatifs : on retombe dans Z (representation
    # symetrique autour de 0) si m est "proche" de n
    if m > n // 2:
        m -= n
    return m


def add_encrypted(pub: dict, c1: int, c2: int) -> int:
    return (c1 * c2) % pub["n2"]


def mul_encrypted_by_scalar(pub: dict, c: int, k: int) -> int:
    n2 = pub["n2"]
    if k >= 0:
        return pow(c, k, n2)
    # E(x)^(-k) mod n^2 = E(-k*x) => on inverse modulaire pour un scalaire negatif
    return pow(_modinv(c, n2), -k, n2)


_KEYS_CACHE: dict | None = None


def get_or_create_keys():
    global _KEYS_CACHE
    if _KEYS_CACHE is None:
        pub, priv = generate_keypair()
        _KEYS_CACHE = (pub, priv)
    return _KEYS_CACHE


def run_paillier_demo(values: list[float], weights: list[float], bias: float) -> dict:
    pub, priv = get_or_create_keys()

    t0 = time.perf_counter()
    int_values = [round(v * SCALE) for v in values]
    ciphertexts = [encrypt(pub, v) for v in int_values]
    t1 = time.perf_counter()

    # --- le "serveur" ne voit QUE pub + ciphertexts + weights (poids publics) ---
    int_weights = [round(w * SCALE) for w in weights]
    weighted_terms = []
    for c, w in zip(ciphertexts, int_weights):
        weighted_terms.append(mul_encrypted_by_scalar(pub, c, w))

    acc = weighted_terms[0]
    for term in weighted_terms[1:]:
        acc = add_encrypted(pub, acc, term)

    # le biais est un scalaire clair -> on l'ajoute en le chiffrant avec r=1
    # (equivalent a E(bias) puis addition homomorphe)
    bias_int = round(bias * SCALE * SCALE)
    encrypted_bias = pow(pub["g"], bias_int, pub["n2"])
    acc_with_bias = add_encrypted(pub, acc, encrypted_bias)
    t2 = time.perf_counter()

    # --- retour cote "client" : dechiffrement ---
    decrypted_scaled = decrypt(pub, priv, acc_with_bias)
    result = decrypted_scaled / (SCALE * SCALE)
    t3 = time.perf_counter()

    plaintext_check = bias + sum(w * v for w, v in zip(weights, values))

    return {
        "step": "paillier",
        "title": "Chiffrement homomorphe partiel (Paillier)",
        "public_key_preview": {
            "n_bits": pub["n"].bit_length(),
            "n_preview": str(pub["n"])[:24] + "...",
        },
        "ciphertext_previews": [str(c)[:32] + "..." for c in ciphertexts],
        "ciphertext_sizes_bytes": [ (c.bit_length() + 7)//8 for c in ciphertexts],
        "server_computation": {
            "description": (
                "Le serveur calcule E(x_i)^(w_i * SCALE) pour chaque feature "
                "(multiplication par un poids CLAIR), puis multiplie tous "
                "les chiffres entre eux (= addition chiffree), sans jamais "
                "voir x_i en clair."
            ),
            "weighted_terms_preview": [str(t)[:32] + "..." for t in weighted_terms],
            "final_ciphertext_preview": str(acc_with_bias)[:32] + "...",
        },
        "decrypted_result": round(result, 4),
        "plaintext_reference": round(plaintext_check, 4),
        "exact_match": abs(result - plaintext_check) < 1e-6,
        "timings_ms": {
            "client_encryption": round((t1 - t0) * 1000, 4),
            "server_homomorphic_computation": round((t2 - t1) * 1000, 4),
            "client_decryption": round((t3 - t2) * 1000, 4),
        },
        "conclusion": (
            "Le serveur a calcule le score EXACT sans jamais voir revenu, "
            "ratio d'endettement ou incidents en clair : seules des additions "
            "et des multiplications par un scalaire connu sont possibles avec "
            "Paillier, mais c'est deja assez pour un score lineaire."
        ),
    }
