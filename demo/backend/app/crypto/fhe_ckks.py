"""
ETAPE 3 - FHE "complet" : le schema CKKS (Cheon-Kim-Kim-Song, 2017) via
Microsoft SEAL (bibliotheque TenSEAL). Contrairement a Paillier, CKKS
supporte addition ET multiplication ENTRE DEUX CHIFFRES, sur des nombres
REELS (approximatifs) -- ce qui permet en theorie des modeles bien plus
riches qu'un score lineaire (reseaux de neurones, regressions logistiques
approchees, etc.), au prix d'un chiffre beaucoup plus gros et d'une
precision approximative (bruit).

Point cle de la demo : on simule VRAIMENT la separation client/serveur.
  - Le CLIENT genere un contexte avec la cle secrete, chiffre son vecteur
    de features, et n'envoie au serveur qu'un contexte PUBLIC (sans cle
    secrete) + le vecteur chiffre.
  - Le SERVEUR calcule le produit scalaire chiffre x poids (poids en clair)
    et ne peut PAS dechiffrer (on le prouve en tentant un dechiffrement
    cote serveur, qui echoue).
  - Seul le CLIENT, qui a garde le contexte complet, peut dechiffrer le
    score final.
"""

import time

import tenseal as ts

POLY_MODULUS_DEGREE = 8192
COEFF_MOD_BIT_SIZES = [60, 40, 40, 60]
GLOBAL_SCALE = 2 ** 40


def _make_client_context() -> ts.Context:
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=POLY_MODULUS_DEGREE,
        coeff_mod_bit_sizes=COEFF_MOD_BIT_SIZES,
    )
    context.generate_galois_keys()
    context.global_scale = GLOBAL_SCALE
    return context


def run_ckks_demo(values: list[float], weights: list[float], bias: float) -> dict:
    # ---------------------------------------------------------------
    # COTE CLIENT : cle secrete generee, vecteur chiffre
    # ---------------------------------------------------------------
    t0 = time.perf_counter()
    client_context = _make_client_context()
    enc_vector_client = ts.ckks_vector(client_context, values)
    t1 = time.perf_counter()

    ciphertext_bytes = enc_vector_client.serialize()
    plaintext_vector_bytes = len(values) * 8  # 8 octets par float64

    # Ce que le client envoie reellement sur le reseau : un contexte PUBLIC
    # (sans cle secrete) + le vecteur chiffre serialise.
    public_context_bytes = client_context.serialize(save_secret_key=False)
    server_context = ts.context_from(public_context_bytes)
    enc_vector_server = ts.ckks_vector_from(server_context, ciphertext_bytes)

    # ---------------------------------------------------------------
    # COTE SERVEUR : calcule le produit scalaire chiffre . poids (clair)
    # ---------------------------------------------------------------
    t2 = time.perf_counter()
    enc_dot = enc_vector_server.dot(weights)
    enc_score = enc_dot + bias  # addition d'une constante publique, toujours chiffree
    t3 = time.perf_counter()

    # Preuve que le serveur ne PEUT PAS dechiffrer (pas de cle secrete)
    server_decrypt_error = None
    try:
        enc_score.decrypt()
        server_decrypt_error = "ATTENTION : le dechiffrement a reussi (bug)."
    except Exception as exc:  # noqa: BLE001 - message pedagogique volontaire
        server_decrypt_error = f"{type(exc).__name__}: dechiffrement impossible sans la cle secrete."

    result_bytes = enc_score.serialize()

    # ---------------------------------------------------------------
    # RETOUR AU CLIENT : reconstruction du chiffre avec le contexte complet
    # ---------------------------------------------------------------
    t4 = time.perf_counter()
    enc_score_client = ts.ckks_vector_from(client_context, result_bytes)
    decrypted = enc_score_client.decrypt()[0]
    t5 = time.perf_counter()

    plaintext_check = bias + sum(w * v for w, v in zip(weights, values))

    return {
        "step": "ckks",
        "title": "FHE complet (CKKS, via Microsoft SEAL / TenSEAL)",
        "params": {
            "poly_modulus_degree": POLY_MODULUS_DEGREE,
            "coeff_mod_bit_sizes": COEFF_MOD_BIT_SIZES,
            "global_scale_log2": 40,
        },
        "sizes_bytes": {
            "plaintext_vector": plaintext_vector_bytes,
            "ciphertext_vector": len(ciphertext_bytes),
            "public_context": len(public_context_bytes),
            "encrypted_result": len(result_bytes),
        },
        "expansion_ratio": round(len(ciphertext_bytes) / plaintext_vector_bytes, 1),
        "server_attempt_to_decrypt": server_decrypt_error,
        "decrypted_result": round(float(decrypted), 4),
        "plaintext_reference": round(plaintext_check, 4),
        "absolute_error": abs(round(float(decrypted) - plaintext_check, 8)),
        "timings_ms": {
            "client_context_and_encryption": round((t1 - t0) * 1000, 4),
            "network_context_transfer_simulated": round((t2 - t1) * 1000, 4),
            "server_homomorphic_dot_product": round((t3 - t2) * 1000, 4),
            "network_result_transfer_simulated": round((t4 - t3) * 1000, 4),
            "client_decryption": round((t5 - t4) * 1000, 4),
        },
        "conclusion": (
            "Le serveur a calcule un produit scalaire chiffre (addition ET "
            "multiplication, sur des reels) sans jamais detenir la cle "
            "secrete : la tentative de dechiffrement cote serveur echoue. "
            "Le resultat n'est qu'APPROXIMATIF (bruit CKKS), et le chiffre "
            "est des milliers de fois plus volumineux que la donnee brute."
        ),
    }
