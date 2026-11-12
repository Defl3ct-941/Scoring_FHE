"""
Client separe : c'est LUI qui detient les cles secretes.

Il tourne dans un autre processus (ou une autre machine) que le serveur, chiffre
les trois indicateurs, n'envoie que des chiffres et du materiel public a l'API
/api/v2, puis dechiffre le resultat localement.

Usage (serveur lance par `docker compose up` ou `uvicorn app.main:app`) :

    cd 04_demo
    python client/client.py --revenu 3200 --endettement 28 --incidents 1
    python client/client.py --schema ckks --mode terms --trace echanges/

--trace ecrit dans un dossier EXACTEMENT ce qui est parti sur le reseau et ce qui
est revenu, pour verifier soi-meme qu'aucune valeur en clair ni cle secrete n'y
figure (partie B du cas pratique).
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app import config, protocol  # noqa: E402
from app.crypto import paillier  # noqa: E402

CKKS_PARAMS = {"poly_modulus_degree": 8192, "coeff_mod_bit_sizes": [60, 40, 40, 60]}
CKKS_SCALE = 2 ** 40


class Trace:
    """Enregistre les octets echanges ; ne recoit jamais de secret."""

    def __init__(self, folder: str | None):
        self.folder = Path(folder) if folder else None
        self.sizes: dict[str, int] = {}
        if self.folder:
            self.folder.mkdir(parents=True, exist_ok=True)

    def record(self, name: str, payload: bytes):
        self.sizes[name] = len(payload)
        if self.folder:
            (self.folder / name).write_bytes(payload)


def _ms(t0: float) -> float:
    return round((time.perf_counter() - t0) * 1000, 3)


def score_paillier(url: str, client: tuple[float, float, int], trace: Trace, key_bits: int = 2048) -> dict:
    timings = {}
    t = time.perf_counter()
    pub, priv = paillier.generate_keypair(key_bits)  # cle secrete : reste ici
    timings["generation_cles_ms"] = _ms(t)

    t = time.perf_counter()
    cts = [paillier.encrypt(pub, m) for m in protocol.encode_features(*client)]
    timings["chiffrement_ms"] = _ms(t)

    body = json.dumps({"n": str(pub["n"]), "ciphertexts": [str(c) for c in cts]}).encode()
    trace.record("paillier_requete.json", body)
    t = time.perf_counter()
    resp = requests.post(f"{url}/api/v2/paillier/score", data=body,
                         headers={"Content-Type": "application/json"}, timeout=60)
    timings["aller_retour_http_ms"] = _ms(t)
    resp.raise_for_status()
    trace.record("paillier_reponse.json", resp.content)

    t = time.perf_counter()
    answer = resp.json()
    score = paillier.decrypt(pub, priv, int(answer["ciphertext"])) / answer["result_scale"]
    timings["dechiffrement_ms"] = _ms(t)
    return {"schema": f"Paillier {pub['n'].bit_length()} bits", "score": score, "temps": timings}


def score_ckks(url: str, client: tuple[float, float, int], trace: Trace, mode: str = "dot") -> dict:
    import tenseal as ts

    timings = {}
    t = time.perf_counter()
    context = ts.context(ts.SCHEME_TYPE.CKKS, **CKKS_PARAMS)  # contient la cle secrete
    context.global_scale = CKKS_SCALE
    if mode == "dot":
        context.generate_galois_keys()
    # Seul ce contexte PUBLIC quitte le client. Pas de cles de relinearisation :
    # le circuit ne multiplie jamais deux chiffres entre eux.
    public_context = context.serialize(
        save_secret_key=False, save_galois_keys=(mode == "dot"), save_relin_keys=False
    )
    timings["generation_cles_ms"] = _ms(t)

    trace.record("ckks_contexte_public.bin", public_context)
    t = time.perf_counter()
    resp = requests.post(f"{url}/api/v2/ckks/session", data=public_context,
                         headers={"Content-Type": "application/octet-stream"}, timeout=300)
    timings["depot_contexte_http_ms"] = _ms(t)
    resp.raise_for_status()
    session_id = resp.json()["session_id"]

    t = time.perf_counter()
    x = config.centered_features(*client)
    ciphertext = ts.ckks_vector(context, x).serialize()
    timings["chiffrement_ms"] = _ms(t)

    trace.record("ckks_requete.bin", ciphertext)
    t = time.perf_counter()
    resp = requests.post(f"{url}/api/v2/ckks/score/{session_id}", params={"mode": mode},
                         data=ciphertext, headers={"Content-Type": "application/octet-stream"},
                         timeout=60)
    timings["aller_retour_http_ms"] = _ms(t)
    resp.raise_for_status()
    trace.record("ckks_reponse.bin", resp.content)

    t = time.perf_counter()
    values = ts.ckks_vector_from(context, resp.content).decrypt()
    score = values[0] if mode == "dot" else config.BIAS + sum(values)
    timings["dechiffrement_ms"] = _ms(t)
    return {"schema": f"CKKS N={CKKS_PARAMS['poly_modulus_degree']} (mode {mode})",
            "score": float(score), "temps": timings}


def main():
    ap = argparse.ArgumentParser(description="Client separe du scoring chiffre")
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--revenu", type=float, default=3200.0)
    ap.add_argument("--endettement", type=float, default=28.0)
    ap.add_argument("--incidents", type=int, default=1)
    ap.add_argument("--schema", choices=["paillier", "ckks", "tous"], default="tous")
    ap.add_argument("--mode", choices=["dot", "terms"], default="dot", help="circuit CKKS")
    ap.add_argument("--trace", help="dossier ou ecrire les octets echanges")
    args = ap.parse_args()

    client = (args.revenu, args.endettement, args.incidents)
    clear = config.plaintext_score(*client)
    encoded = protocol.encoded_reference(*client)
    trace = Trace(args.trace)

    results = []
    if args.schema in ("paillier", "tous"):
        results.append(score_paillier(args.url, client, trace))
    if args.schema in ("ckks", "tous"):
        results.append(score_ckks(args.url, client, trace, args.mode))

    print(f"Formule en clair (calcul local de controle) : {clear!r}")
    print(f"Reference encodee au millieme               : {encoded!r}")
    for r in results:
        print(f"\n{r['schema']}")
        print(f"  score dechiffre               : {r['score']!r}")
        print(f"  ecart a la formule en clair   : {abs(r['score'] - clear):.3e}")
        print(f"  ecart a la reference encodee  : {abs(r['score'] - encoded):.3e}")
        for k, v in r["temps"].items():
            print(f"  {k:<28}: {v}")
    print("\nOctets echanges avec le serveur :")
    for name, size in trace.sizes.items():
        print(f"  {name:<28}: {size:>10} o")
    if trace.folder:
        print(f"\nEchanges enregistres dans {trace.folder}/")


if __name__ == "__main__":
    main()
