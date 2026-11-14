"""
Mesures alignees (remplace la methode de benchmark.py, conserve pour l'historique).

Ce que cette version corrige :
  - le temps "serveur Paillier" ne contient plus le rechiffrement aleatoire du
    biais (qui pesait ~96 % du temps mesure) ; il est mesure a part ;
  - memes frontieres pour les deux schemas : cles / chiffrement / calcul serveur /
    dechiffrement, chacune avec le meme nombre de repetitions, apres echauffement,
    dans un ordre alterne ;
  - tous les echantillons bruts sont conserves (CSV) ; mediane, quartiles, extremes ;
  - le calcul en clair, trop court pour le chronometre, est mesure par lots ;
  - erreurs mesurees sur des profils synthetiques, en separant l'erreur d'encodage
    (arrondi au millieme) de l'erreur du calcul chiffre ;
  - taille du contexte CKKS selon les cles d'evaluation reellement necessaires.

Usage (depuis la racine du depot, dans l'environnement de 04_demo/backend) :
    python 05_poster/scripts/benchmark_v2.py
Ecrit 05_poster/data/mesures_v2.json et mesures_v2_echantillons.csv.
Les profils sont synthetiques : ils testent la precision numerique, pas la
qualite d'un modele de risque.
"""

import csv
import json
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_demo" / "backend"))

import tenseal as ts  # noqa: E402

from app import config, protocol  # noqa: E402
from app.crypto import paillier  # noqa: E402

RUNS = 30
KEYGEN_RUNS = 10
CLIENT = (3200.0, 28.0, 1)
N_PROFILS_CKKS = 1000
N_PROFILS_PAILLIER = 50
CLEAR_BATCH = 100_000
CKKS = {"poly_modulus_degree": 8192, "coeff_mod_bit_sizes": [60, 40, 40, 60]}
CKKS_SCALE = 2 ** 40


def _sh(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        return ""


def machine():
    cpu = _sh("sysctl", "-n", "machdep.cpu.brand_string") or platform.processor()
    if not cpu and Path("/proc/cpuinfo").exists():
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    ram = _sh("sysctl", "-n", "hw.memsize")
    return {
        "systeme": f"{platform.system()} {platform.release()} {platform.machine()}",
        "cpu": cpu,
        "coeurs_logiques": os.cpu_count(),
        "ram_go": round(int(ram) / 2 ** 30, 1) if ram.isdigit() else None,
        "python": platform.python_version(),
        "tenseal": ts.__version__,
        "commit": _sh("git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"),
        "arbre_modifie": bool(_sh("git", "-C", str(ROOT), "status", "--porcelain")),
        "date": time.strftime("%Y-%m-%d %H:%M"),
    }


def measure(phases: dict, runs: int) -> dict:
    """Chronometre chaque phase `runs` fois, en alternant les phases a chaque tour."""
    for fn in phases.values():
        fn()  # echauffement
    samples = {name: [] for name in phases}
    for _ in range(runs):
        for name, fn in phases.items():
            t = time.perf_counter()
            fn()
            samples[name].append((time.perf_counter() - t) * 1000)
    return samples


def stats(values: list[float]) -> dict:
    q = statistics.quantiles(values, n=4)
    return {"mediane_ms": statistics.median(values), "q1_ms": q[0], "q3_ms": q[2],
            "min_ms": min(values), "max_ms": max(values), "n": len(values)}


def profils(n: int, seed: int = 2027):
    rng = random.Random(seed)
    return [(round(rng.uniform(1000, 8000), 2), round(rng.uniform(0, 60), 4), rng.randint(0, 5))
            for _ in range(n)]


def paillier_server(pub, cts, fresh_bias: bool):
    n, n2 = pub["n"], pub["n2"]
    b = protocol.encoded_bias()
    acc = paillier.encrypt(pub, b) if fresh_bias else (1 + b * n) % n2
    for c, w in zip(cts, protocol.encoded_weights()):
        acc = paillier.add_encrypted(pub, acc, paillier.mul_encrypted_by_scalar(pub, c, w))
    return acc


def nbytes(i: int) -> int:
    return (i.bit_length() + 7) // 8


def main():
    all_samples: dict[str, list[float]] = {}
    out = {"client": dict(zip(["revenu", "ratio_endettement", "incidents"], CLIENT)),
           "machine": machine(),
           "methode": {"repetitions": RUNS, "repetitions_generation_cles": KEYGEN_RUNS,
                       "echauffement": "1 execution par phase, non comptee",
                       "ordre": "phases alternees a chaque tour",
                       "horloge": "time.perf_counter, un seul processus, sans reseau"}}

    # ------------------------------------------------------------------ clair
    def clear_batch():
        f = config.plaintext_score
        for _ in range(CLEAR_BATCH):
            f(*CLIENT)

    s = measure({"clair_lot": clear_batch}, RUNS)["clair_lot"]
    per_call_us = [v / CLEAR_BATCH * 1000 for v in s]
    all_samples["clair_par_score_us"] = per_call_us
    out["clair"] = {"score": config.plaintext_score(*CLIENT),
                    "par_score_us_mediane": statistics.median(per_call_us),
                    "taille_lot": CLEAR_BATCH, "octets_entree": 3 * 8}

    # --------------------------------------------------------------- Paillier
    keygen = measure({"paillier_generation_cles": lambda: paillier.generate_keypair(2048)},
                     KEYGEN_RUNS)
    all_samples.update(keygen)
    pub, priv = paillier.generate_keypair(2048)
    xi = protocol.encode_features(*CLIENT)
    cts = [paillier.encrypt(pub, v) for v in xi]
    res = paillier_server(pub, cts, fresh_bias=False)
    p = measure({
        "paillier_chiffrement_3_valeurs": lambda: [paillier.encrypt(pub, v) for v in xi],
        "paillier_serveur": lambda: paillier_server(pub, cts, False),
        "paillier_serveur_avec_rechiffrement_du_biais": lambda: paillier_server(pub, cts, True),
        "paillier_dechiffrement": lambda: paillier.decrypt(pub, priv, res),
    }, RUNS)
    all_samples.update(p)
    score_p = paillier.decrypt(pub, priv, res) / protocol.RESULT_SCALE
    out["paillier"] = {
        "cle_bits": pub["n"].bit_length(),
        "score": score_p,
        "octets_cle_publique": nbytes(pub["n"]),
        "octets_entree_chiffree": sum(nbytes(c) for c in cts),
        "octets_resultat_chiffre": nbytes(res),
        "temps": {k.removeprefix("paillier_"): stats(v) for k, v in {**keygen, **p}.items()},
    }

    # ------------------------------------------------------------------- CKKS
    def make_ctx(galois=True):
        c = ts.context(ts.SCHEME_TYPE.CKKS, **CKKS)
        c.global_scale = CKKS_SCALE
        if galois:
            c.generate_galois_keys()
        return c

    keygen = measure({"ckks_generation_cles_avec_rotations": lambda: make_ctx(True),
                      "ckks_generation_cles_sans_rotations": lambda: make_ctx(False)}, KEYGEN_RUNS)
    all_samples.update(keygen)
    ctx = make_ctx(True)
    x = config.centered_features(*CLIENT)
    w = config.WEIGHTS_VECTOR
    ct = ts.ckks_vector(ctx, x).serialize()
    sizes = {
        "octets_contexte_public_tel_que_poster": len(ctx.serialize(save_secret_key=False)),
        "octets_contexte_public_sans_relinearisation": len(
            ctx.serialize(save_secret_key=False, save_relin_keys=False)),
        "octets_contexte_public_sans_rotations": len(
            ctx.serialize(save_secret_key=False, save_galois_keys=False, save_relin_keys=False)),
    }
    srv_ctx = ts.context_from(ctx.serialize(save_secret_key=False, save_relin_keys=False))
    srv_vec = ts.ckks_vector_from(srv_ctx, ct)
    res_dot = (srv_vec.dot(w) + config.BIAS).serialize()
    res_terms = (srv_vec * w).serialize()
    c = measure({
        "ckks_chiffrement_et_serialisation": lambda: ts.ckks_vector(ctx, x).serialize(),
        "ckks_serveur_produit_scalaire": lambda: srv_vec.dot(w) + config.BIAS,
        "ckks_serveur_terme_a_terme": lambda: srv_vec * w,
        "ckks_serveur_lecture_du_chiffre": lambda: ts.ckks_vector_from(srv_ctx, ct),
        "ckks_dechiffrement_produit_scalaire": lambda: ts.ckks_vector_from(ctx, res_dot).decrypt()[0],
        "ckks_dechiffrement_terme_a_terme": lambda: config.BIAS + sum(
            ts.ckks_vector_from(ctx, res_terms).decrypt()),
    }, RUNS)
    all_samples.update(c)
    out["ckks"] = {
        **CKKS, "echelle_log2": 40,
        "score": float(ts.ckks_vector_from(ctx, res_dot).decrypt()[0]),
        "octets_entree_chiffree": len(ct),
        "octets_resultat_produit_scalaire": len(res_dot),
        "octets_resultat_terme_a_terme": len(res_terms),
        **sizes,
        "temps": {k.removeprefix("ckks_"): stats(v) for k, v in {**keygen, **c}.items()},
    }

    # ----------------------------------------------------------------- erreurs
    ps = profils(N_PROFILS_CKKS)
    enc_err = [abs(protocol.encoded_reference(*q) - config.plaintext_score(*q)) for q in ps]
    ckks_err, ckks_terms_err = [], []
    for q in ps:
        v = ts.ckks_vector_from(srv_ctx, ts.ckks_vector(ctx, config.centered_features(*q)).serialize())
        ref = config.plaintext_score(*q)
        ckks_err.append(abs(ts.ckks_vector_from(ctx, (v.dot(w) + config.BIAS).serialize()).decrypt()[0] - ref))
        ckks_terms_err.append(abs(config.BIAS + sum(ts.ckks_vector_from(ctx, (v * w).serialize()).decrypt()) - ref))
    pai_mismatch = 0
    for q in ps[:N_PROFILS_PAILLIER]:
        cq = [paillier.encrypt(pub, v) for v in protocol.encode_features(*q)]
        got = paillier.decrypt(pub, priv, paillier_server(pub, cq, False)) / protocol.RESULT_SCALE
        pai_mismatch += got != protocol.encoded_reference(*q)

    def err(v):
        s_ = sorted(v)
        return {"mediane": statistics.median(v), "p95": s_[int(0.95 * len(s_))], "max": max(v), "n": len(v)}

    out["erreurs"] = {
        "profils": "synthetiques, graine 2027 : revenu 1000-8000 (centimes), "
                   "endettement 0-60 (4 decimales), incidents 0-5",
        "encodage_au_millieme_vs_formule_en_clair": err(enc_err),
        "paillier_vs_reference_encodee": {"ecarts_non_nuls": pai_mismatch, "n": N_PROFILS_PAILLIER},
        "ckks_produit_scalaire_vs_formule_en_clair": err(ckks_err),
        "ckks_terme_a_terme_vs_formule_en_clair": err(ckks_terms_err),
    }

    data = ROOT / "05_poster" / "data"
    data.mkdir(parents=True, exist_ok=True)
    (data / "mesures_v2.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with (data / "mesures_v2_echantillons.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["mesure", "repetition", "valeur", "unite"])
        for name, vals in all_samples.items():
            unit = "us" if name.endswith("_us") else "ms"
            for i, v in enumerate(vals, 1):
                wr.writerow([name, i, f"{v:.6f}", unit])
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
