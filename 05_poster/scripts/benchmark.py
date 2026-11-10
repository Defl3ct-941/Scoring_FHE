"""
Mesures affichées sur le poster (encadré « Résultats »).

Reprend le modèle de scoring et les briques cryptographiques de 04_demo et mesure,
pour un même client (revenu, taux d'endettement, incidents) :
  - le temps du score en clair, avec Paillier (clé 2048 bits) et avec CKKS (TenSEAL) ;
  - la taille des données envoyées au serveur ;
  - l'erreur sur le score déchiffré.

Usage (depuis la racine du dépôt) :
    pip install tenseal pycryptodome
    python 05_poster/scripts/benchmark.py            # écrit 05_poster/data/mesures.json
"""

import json
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_demo" / "backend"))

import tenseal as ts  # noqa: E402

from app import config  # noqa: E402
from app.crypto import paillier  # noqa: E402

RUNS = 20
CLIENT = (3200.0, 28.0, 1.0)  # revenu, taux d'endettement (%), incidents


def median_ms(fn, runs=RUNS):
    out = []
    for _ in range(runs):
        t = time.perf_counter()
        fn()
        out.append((time.perf_counter() - t) * 1000)
    return statistics.median(out)


def bench_clear():
    ref = config.plaintext_score(*CLIENT)
    t = median_ms(lambda: config.plaintext_score(*CLIENT), runs=2000)
    return {"score": ref, "server_ms": t, "client_bytes": 3 * 8}


def bench_paillier(bits=2048):
    pub, priv = paillier.generate_keypair(bits)
    x = config.centered_features(*CLIENT)
    s = paillier.SCALE
    xi = [round(v * s) for v in x]
    wi = [round(w * s) for w in config.WEIGHTS_VECTOR]
    n = pub["n"]

    def enc():
        return [paillier.encrypt(pub, v) for v in xi]

    cts = enc()

    def server():
        acc = paillier.encrypt(pub, round(config.BIAS * s * s))
        for c, w in zip(cts, wi):
            acc = paillier.add_encrypted(pub, acc, paillier.mul_encrypted_by_scalar(pub, c, w))
        return acc

    res = server()

    def dec():
        v = paillier.decrypt(pub, priv, res)
        if v > n // 2:
            v -= n
        return v / (s * s)

    score = dec()
    size = sum((c.bit_length() + 7) // 8 for c in cts)
    return {
        "key_bits": bits,
        "encrypt_ms": median_ms(enc, 10),
        "server_ms": median_ms(server, 10),
        "decrypt_ms": median_ms(dec, 10),
        "client_bytes": size,
        "score": score,
    }


def bench_ckks():
    def make_ctx():
        c = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192,
                       coeff_mod_bit_sizes=[60, 40, 40, 60])
        c.generate_galois_keys()
        c.global_scale = 2 ** 40
        return c

    ctx = make_ctx()
    x = config.centered_features(*CLIENT)
    w = config.WEIGHTS_VECTOR
    enc_vec = ts.ckks_vector(ctx, x)
    ct = enc_vec.serialize()
    pub_ctx = ctx.serialize(save_secret_key=False, save_galois_keys=True, save_relin_keys=True)
    srv_ctx = ts.context_from(pub_ctx)
    srv_vec = ts.ckks_vector_from(srv_ctx, ct)

    def server():
        return srv_vec.dot(w) + config.BIAS

    res = server().serialize()

    def dec():
        return ts.ckks_vector_from(ctx, res).decrypt()[0]

    score = dec()
    return {
        "poly_modulus_degree": 8192,
        "keygen_ms": median_ms(make_ctx, 5),
        "encrypt_ms": median_ms(lambda: ts.ckks_vector(ctx, x), 20),
        "server_ms": median_ms(server, 20),
        "decrypt_ms": median_ms(dec, 20),
        "client_bytes": len(ct),
        "public_context_bytes": len(pub_ctx),
        "result_bytes": len(res),
        "score": score,
    }


def main():
    clear = bench_clear()
    pai = bench_paillier()
    ckks = bench_ckks()
    ref = clear["score"]
    pai["abs_error"] = abs(pai["score"] - ref)
    ckks["abs_error"] = abs(ckks["score"] - ref)
    out = {
        "client": dict(zip(["revenu", "ratio_endettement", "incidents"], CLIENT)),
        "machine": f"{platform.system()} {platform.machine()}, Python {platform.python_version()}, TenSEAL {ts.__version__}",
        "clear": clear,
        "paillier": pai,
        "ckks": ckks,
    }
    dest = ROOT / "05_poster" / "data" / "mesures.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
