"""
ETAPE 1 - Chiffrement "classique" (symetrique, authentifie).

Objectif pedagogique : montrer que le chiffrement qu'on utilise tous les
jours (TLS, disque chiffre, etc.) protege une donnee AU REPOS et EN TRANSIT,
mais interdit tout calcul dessus. Des qu'on modifie un octet du chiffre,
soit on obtient un dechiffrement invalide (cas authentifie, Fernet/AES-GCM),
soit -- avec un chiffrement non authentifie -- un dechiffrement qui reussit
mais renvoie n'importe quoi. Dans les deux cas : impossible de calculer
correctement "a l'aveugle".
"""

import time

from cryptography.fernet import Fernet, InvalidToken


def run_classic_demo(values: list[float]) -> dict:
    key = Fernet.generate_key()
    fernet = Fernet(key)

    t0 = time.perf_counter()
    ciphertexts = []
    for v in values:
        # on encode la valeur (multipliee par 100 pour garder 2 decimales)
        # comme des octets avant de chiffrer, comme le ferait une vraie appli
        payload = str(round(v * 100)).encode()
        token = fernet.encrypt(payload)
        ciphertexts.append(token)
    t1 = time.perf_counter()

    total_ciphertext_bytes = sum(len(c) for c in ciphertexts)

    # Le "serveur" tente d'additionner les DEUX PREMIERS chiffres tel quel,
    # octet par octet (c'est la seule chose qu'un serveur aveugle pourrait
    # essayer de faire sans la cle).
    attempt_error = None
    forged = None
    if len(ciphertexts) >= 2:
        a, b = ciphertexts[0], ciphertexts[1]
        n = min(len(a), len(b))
        forged = bytes((a[i] + b[i]) % 256 for i in range(n))
        try:
            fernet.decrypt(forged)
        except InvalidToken:
            attempt_error = (
                "InvalidToken : le jeton falsifie est rejete. Fernet est un "
                "chiffrement AUTHENTIFIE (AES-128-CBC + HMAC) : la moindre "
                "alteration du chiffre est detectee et le dechiffrement est "
                "purement et simplement refuse."
            )

    t2 = time.perf_counter()

    return {
        "step": "classique",
        "title": "Chiffrement classique (Fernet / AES authentifie)",
        "inputs": values,
        "ciphertext_previews": [c.decode()[:48] + "..." for c in ciphertexts],
        "ciphertext_sizes_bytes": [len(c) for c in ciphertexts],
        "total_ciphertext_bytes": total_ciphertext_bytes,
        "server_attempt": {
            "description": (
                "Le serveur essaie d'additionner les octets bruts des deux "
                "premiers chiffres pour simuler 'chiffre_A + chiffre_B'."
            ),
            "forged_preview": forged.hex()[:48] + "..." if forged else None,
            "result": attempt_error or "Le calcul sur le chiffre echoue.",
            "computation_possible": False,
        },
        "timings_ms": {
            "encryption": round((t1 - t0) * 1000, 4),
            "server_attempt": round((t2 - t1) * 1000, 4),
        },
        "conclusion": (
            "Avec un chiffrement classique, la confidentialite est totale au "
            "repos/en transit, mais AUCUN calcul n'est possible sur les "
            "donnees chiffrees : il faut les dechiffrer d'abord, ce qui "
            "oblige le serveur a voir les valeurs en clair."
        ),
    }
