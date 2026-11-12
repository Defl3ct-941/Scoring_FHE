"""
API "v2" : le serveur de calcul tel qu'un prestataire le deploierait.

Difference avec les routes /api/step/* (demonstration pas a pas, ou client et
serveur sont simules dans le meme processus et ou l'API recoit les valeurs en
clair) : ici le serveur ne recoit QUE
  - du materiel public (module Paillier n, ou contexte CKKS sans cle secrete) ;
  - des chiffres.
Il ne genere aucune cle, n'importe aucune fonction de dechiffrement et renvoie
un chiffre. Le client (04_demo/client/client.py) tourne dans un autre processus,
garde la cle secrete et dechiffre lui-meme.

Ce que cela garantit : un serveur honnete-mais-curieux n'apprend pas les entrees.
Ce que cela ne garantit PAS : que le serveur a applique le bon modele (integrite),
que les entrees sont vraies, ni la protection des metadonnees (tailles, horaires).
"""

import secrets
from collections import OrderedDict

import tenseal as ts
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from app import config, protocol
from app.crypto.paillier import add_encrypted, mul_encrypted_by_scalar

router = APIRouter(prefix="/api/v2", tags=["serveur sans cle secrete"])

MODEL_VERSION = "lineaire-demo-1"
PAILLIER_MIN_BITS = 2048
CKKS_MAX_CONTEXT_BYTES = 64 * 1024 * 1024
CKKS_MAX_CIPHERTEXT_BYTES = 4 * 1024 * 1024
CKKS_MAX_SESSIONS = 8

# session_id -> contexte public. Borne pour qu'un client ne sature pas la memoire.
_CKKS_SESSIONS: "OrderedDict[str, ts.Context]" = OrderedDict()


# ------------------------------------------------------------------ Paillier
class PaillierRequest(BaseModel):
    n: str = Field(..., description="Module public n, en decimal")
    ciphertexts: list[str] = Field(..., min_length=3, max_length=3)


def _parse_int(text: str, name: str) -> int:
    if not text.isascii() or not text.isdigit() or len(text) > 2500:
        raise HTTPException(422, f"{name} : entier decimal positif attendu")
    return int(text)


@router.post("/paillier/score")
def paillier_score(req: PaillierRequest):
    n = _parse_int(req.n, "n")
    if n.bit_length() < PAILLIER_MIN_BITS - 1:
        raise HTTPException(422, f"module trop court : {PAILLIER_MIN_BITS} bits minimum")
    if n // 2 <= protocol.max_encoded_magnitude():
        raise HTTPException(422, "module trop petit pour le domaine du score")
    n2 = n * n
    pub = {"n": n, "n2": n2}

    cts = [_parse_int(c, "chiffre") for c in req.ciphertexts]
    if any(not 0 < c < n2 for c in cts):
        raise HTTPException(422, "chiffre hors de l'intervalle ]0, n^2[")

    # Le biais est public : on l'ajoute comme (1 + n)^b = 1 + b*n mod n^2, sans alea.
    # L'alea du resultat vient des chiffres du client. Le resultat n'est pas
    # re-randomise : inutile ici puisque les poids sont publics.
    acc = (1 + protocol.encoded_bias() * n) % n2
    try:
        for c, w in zip(cts, protocol.encoded_weights()):
            acc = add_encrypted(pub, acc, mul_encrypted_by_scalar(pub, c, w))
    except ValueError as exc:  # chiffre non inversible modulo n^2
        raise HTTPException(422, "chiffre invalide") from exc

    return {
        "ciphertext": str(acc),
        "result_scale": protocol.RESULT_SCALE,
        "model_version": MODEL_VERSION,
    }


# ---------------------------------------------------------------------- CKKS
async def _read_body(request: Request, limit: int) -> bytes:
    body = await request.body()
    if not body or len(body) > limit:
        raise HTTPException(413 if body else 422, "corps de requete vide ou trop volumineux")
    return body


@router.post("/ckks/session")
async def ckks_open_session(request: Request):
    """Depot, une fois, du contexte PUBLIC du client (parametres + cles d'evaluation)."""
    raw = await _read_body(request, CKKS_MAX_CONTEXT_BYTES)
    try:
        context = ts.context_from(raw)
    except Exception as exc:  # noqa: BLE001 - TenSEAL leve des types varies
        raise HTTPException(422, "contexte CKKS illisible") from exc
    if context.has_secret_key():
        # Un client qui envoie sa cle secrete a casse le protocole : on refuse
        # plutot que de la conserver.
        raise HTTPException(422, "le contexte contient une cle secrete : refuse")

    session_id = secrets.token_urlsafe(16)
    _CKKS_SESSIONS[session_id] = context
    while len(_CKKS_SESSIONS) > CKKS_MAX_SESSIONS:
        _CKKS_SESSIONS.popitem(last=False)
    return {
        "session_id": session_id,
        "has_galois_keys": context.has_galois_keys(),
        "context_bytes": len(raw),
        "model_version": MODEL_VERSION,
    }


@router.post("/ckks/score/{session_id}")
async def ckks_score(session_id: str, request: Request, mode: str = "dot"):
    """mode=dot  : produit scalaire complet (rotations -> cles de Galois requises).
    mode=terms : poids x entrees terme a terme ; le client additionne apres
                 dechiffrement. Aucune rotation, donc aucun cle de Galois a envoyer.
                 Les poids etant publics, le client n'apprend rien de plus."""
    context = _CKKS_SESSIONS.get(session_id)
    if context is None:
        raise HTTPException(404, "session inconnue ou expiree")
    if mode not in ("dot", "terms"):
        raise HTTPException(422, "mode attendu : dot ou terms")
    if mode == "dot" and not context.has_galois_keys():
        raise HTTPException(422, "mode dot impossible sans cles de Galois")

    raw = await _read_body(request, CKKS_MAX_CIPHERTEXT_BYTES)
    try:
        enc = ts.ckks_vector_from(context, raw)
        if enc.size() != len(config.WEIGHTS_VECTOR):
            raise ValueError("dimension")
        if mode == "dot":
            out = enc.dot(config.WEIGHTS_VECTOR) + config.BIAS
        else:
            out = enc * config.WEIGHTS_VECTOR
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(422, "chiffre CKKS invalide pour cette session") from exc

    return Response(
        content=out.serialize(),
        media_type="application/octet-stream",
        headers={"X-Model-Version": MODEL_VERSION, "X-Mode": mode},
    )
