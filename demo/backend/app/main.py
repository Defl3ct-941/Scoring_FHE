from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import config
from app.crypto import classic_aes, fhe_ckks, paillier

app = FastAPI(title="FHE Scoring Demo")

STATIC_DIR = "app/static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ScoringInput(BaseModel):
    revenu: float = Field(..., ge=0)
    ratio_endettement: float = Field(..., ge=0, le=100)
    incidents: float = Field(..., ge=0)


@app.get("/")
def index():
    return FileResponse(f"{STATIC_DIR}/index.html")


@app.get("/api/model")
def get_model():
    return {
        "features": config.FEATURES,
        "weights": config.WEIGHTS_VECTOR,
        "bias": config.BIAS,
    }


@app.post("/api/step/classic")
def step_classic(inp: ScoringInput):
    raw_values = [inp.revenu, inp.ratio_endettement, inp.incidents]
    return classic_aes.run_classic_demo(raw_values)


@app.post("/api/step/paillier")
def step_paillier(inp: ScoringInput):
    values = config.centered_features(inp.revenu, inp.ratio_endettement, inp.incidents)
    return paillier.run_paillier_demo(values, config.WEIGHTS_VECTOR, config.BIAS)


@app.post("/api/step/ckks")
def step_ckks(inp: ScoringInput):
    values = config.centered_features(inp.revenu, inp.ratio_endettement, inp.incidents)
    return fhe_ckks.run_ckks_demo(values, config.WEIGHTS_VECTOR, config.BIAS)


@app.post("/api/compare")
def compare(inp: ScoringInput):
    raw_values = [inp.revenu, inp.ratio_endettement, inp.incidents]
    values = config.centered_features(inp.revenu, inp.ratio_endettement, inp.incidents)

    classic = classic_aes.run_classic_demo(raw_values)
    pail = paillier.run_paillier_demo(values, config.WEIGHTS_VECTOR, config.BIAS)
    ckks = fhe_ckks.run_ckks_demo(values, config.WEIGHTS_VECTOR, config.BIAS)

    plaintext_score = config.plaintext_score(
        inp.revenu, inp.ratio_endettement, inp.incidents
    )

    return {
        "plaintext_score": round(plaintext_score, 4),
        "classic": {
            "peut_calculer": False,
            "temps_ms": sum(classic["timings_ms"].values()),
            "taille_chiffre_octets": classic["total_ciphertext_bytes"],
            "precision": "exacte (mais calcul impossible)",
        },
        "paillier": {
            "peut_calculer": True,
            "temps_ms": round(sum(pail["timings_ms"].values()), 4),
            "taille_chiffre_octets": sum(pail["ciphertext_sizes_bytes"]),
            "precision": "exacte",
            "resultat": pail["decrypted_result"],
            "operations_supportees": "addition, multiplication par un scalaire clair",
        },
        "ckks": {
            "peut_calculer": True,
            "temps_ms": round(sum(ckks["timings_ms"].values()), 4),
            "taille_chiffre_octets": ckks["sizes_bytes"]["ciphertext_vector"],
            "precision": f"approchee (erreur ~{ckks['absolute_error']:.2e})",
            "resultat": ckks["decrypted_result"],
            "operations_supportees": "addition et multiplication entre deux chiffres, sur des reels",
        },
    }
