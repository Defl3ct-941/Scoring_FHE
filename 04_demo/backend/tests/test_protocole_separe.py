"""
Tests du protocole separe (/api/v2) et de l'encodage.

    cd 04_demo/backend && python -m pytest tests -q

Le "client" des tests garde ses cles dans le test ; le serveur n'est joint que
par des requetes HTTP (TestClient), comme le ferait 04_demo/client/client.py.
"""

import inspect
import json

import pytest
import tenseal as ts
from fastapi.testclient import TestClient

from app import config, protocol, remote
from app.crypto import paillier
from app.main import app

api = TestClient(app)

PROFILS = [
    (3200.0, 28.0, 1),      # cas nominal du poster : 18,3
    (2500.0, 0.0, 0),       # revenu centre nul, aucun incident : 50
    (1000.0, 60.0, 5),      # score tres negatif
    (8000.0, 0.0, 0),       # score eleve
    (0.0, 100.0, 50),       # bornes du domaine
    (100_000.0, 0.0, 0),
    (3200.0, 28.0001, 1),   # decimale sous le pas d'encodage
    (2499.9996, 33.3335, 2),
]


@pytest.fixture(scope="module")
def cles_paillier():
    return paillier.generate_keypair(2048)


@pytest.fixture(scope="module")
def contexte_ckks():
    ctx = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192,
                     coeff_mod_bit_sizes=[60, 40, 40, 60])
    ctx.global_scale = 2 ** 40
    ctx.generate_galois_keys()
    return ctx


def _requete_paillier(pub, client):
    cts = [paillier.encrypt(pub, m) for m in protocol.encode_features(*client)]
    return {"n": str(pub["n"]), "ciphertexts": [str(c) for c in cts]}


# ------------------------------------------------------------------ encodage
def test_cas_nominal_du_poster():
    assert config.plaintext_score(3200.0, 28.0, 1) == pytest.approx(18.3)
    assert protocol.encoded_reference(3200.0, 28.0, 1) == 18.3


def test_exact_ne_vaut_que_pour_les_entiers_encodes():
    clair = config.plaintext_score(3200.0, 28.0001, 1)
    encode = protocol.encoded_reference(3200.0, 28.0001, 1)
    assert encode == 18.3
    assert abs(clair - encode) == pytest.approx(9e-5, rel=1e-3)


def test_le_domaine_tient_dans_le_module():
    assert protocol.max_encoded_magnitude() < 2 ** 64  # tres loin de n/2 (2047 bits)


# ------------------------------------------------------------------ Paillier
@pytest.mark.parametrize("client", PROFILS)
def test_paillier_separe_egale_la_reference_encodee(cles_paillier, client):
    pub, priv = cles_paillier
    rep = api.post("/api/v2/paillier/score", json=_requete_paillier(pub, client))
    assert rep.status_code == 200
    data = rep.json()
    score = paillier.decrypt(pub, priv, int(data["ciphertext"])) / data["result_scale"]
    assert score == protocol.encoded_reference(*client)  # egalite stricte


def test_paillier_la_requete_ne_contient_ni_clair_ni_secret(cles_paillier):
    pub, priv = cles_paillier
    corps = json.dumps(_requete_paillier(pub, (3200.0, 28.0, 1)))
    assert set(json.loads(corps)) == {"n", "ciphertexts"}
    assert str(priv["lam"]) not in corps and str(priv["mu"]) not in corps
    for clair in ("3200", "700000", "28000"):
        assert f'"{clair}"' not in corps


def test_paillier_chiffrement_probabiliste(cles_paillier):
    pub, _ = cles_paillier
    assert paillier.encrypt(pub, 42) != paillier.encrypt(pub, 42)
    assert "random." not in inspect.getsource(paillier.encrypt)


@pytest.mark.parametrize("corps", [
    {"n": "15", "ciphertexts": ["2", "3", "4"]},                 # module ridicule
    {"n": "abc", "ciphertexts": ["2", "3", "4"]},
    {"n": "-5", "ciphertexts": ["2", "3", "4"]},
])
def test_paillier_refuse_les_modules_invalides(corps):
    assert api.post("/api/v2/paillier/score", json=corps).status_code == 422


def test_paillier_refuse_les_chiffres_invalides(cles_paillier):
    pub, _ = cles_paillier
    n = str(pub["n"])
    for cts in (["0", "1", "1"], [str(pub["n2"]), "1", "1"], ["1", "1"], ["1", "1", "x"]):
        assert api.post("/api/v2/paillier/score", json={"n": n, "ciphertexts": cts}).status_code == 422


# ---------------------------------------------------------------------- CKKS
def _session(ctx, galois=True):
    public = ctx.serialize(save_secret_key=False, save_galois_keys=galois, save_relin_keys=False)
    rep = api.post("/api/v2/ckks/session", content=public)
    assert rep.status_code == 200
    return rep.json()["session_id"], public


@pytest.mark.parametrize("client", PROFILS)
def test_ckks_separe_dans_la_tolerance(contexte_ckks, client):
    sid, _ = _session(contexte_ckks)
    chiffre = ts.ckks_vector(contexte_ckks, config.centered_features(*client)).serialize()
    rep = api.post(f"/api/v2/ckks/score/{sid}", content=chiffre)
    assert rep.status_code == 200
    score = ts.ckks_vector_from(contexte_ckks, rep.content).decrypt()[0]
    assert abs(score - config.plaintext_score(*client)) < 1e-3


def test_ckks_mode_terms_sans_cles_de_galois(contexte_ckks):
    sid, public = _session(contexte_ckks, galois=False)
    assert len(public) < 1_000_000  # contre ~35 Mo avec les cles de rotation
    client = (3200.0, 28.0, 1)
    chiffre = ts.ckks_vector(contexte_ckks, config.centered_features(*client)).serialize()
    assert api.post(f"/api/v2/ckks/score/{sid}", content=chiffre).status_code == 422  # dot impossible
    rep = api.post(f"/api/v2/ckks/score/{sid}?mode=terms", content=chiffre)
    termes = ts.ckks_vector_from(contexte_ckks, rep.content).decrypt()
    assert abs(config.BIAS + sum(termes) - 18.3) < 1e-3


def test_ckks_le_serveur_refuse_une_cle_secrete(contexte_ckks):
    avec_secret = contexte_ckks.serialize(save_secret_key=True)
    assert api.post("/api/v2/ckks/session", content=avec_secret).status_code == 422


def test_ckks_le_serveur_ne_peut_pas_dechiffrer(contexte_ckks):
    sid, _ = _session(contexte_ckks)
    ctx_serveur = remote._CKKS_SESSIONS[sid]
    assert not ctx_serveur.has_secret_key()
    chiffre = ts.ckks_vector(contexte_ckks, [700.0, 28.0, 1.0]).serialize()
    with pytest.raises(ValueError):
        ts.ckks_vector_from(ctx_serveur, chiffre).decrypt()


def test_ckks_entrees_invalides(contexte_ckks):
    assert api.post("/api/v2/ckks/session", content=b"pas un contexte").status_code == 422
    assert api.post("/api/v2/ckks/score/inconnue", content=b"x").status_code == 404
    sid, _ = _session(contexte_ckks)
    assert api.post(f"/api/v2/ckks/score/{sid}", content=b"pas un chiffre").status_code == 422
    mauvais = ts.ckks_vector(contexte_ckks, [1.0, 2.0]).serialize()  # mauvaise dimension
    assert api.post(f"/api/v2/ckks/score/{sid}", content=mauvais).status_code == 422


# --------------------------------------------------- separation et demo web
def test_le_module_serveur_n_importe_ni_keygen_ni_dechiffrement():
    source = inspect.getsource(remote)
    for interdit in ("generate_keypair", "decrypt", "secret_key(", "get_or_create_keys"):
        assert interdit not in source.replace("has_secret_key()", "")


@pytest.mark.parametrize("corps", [
    {"revenu": 3200, "ratio_endettement": 28, "incidents": 1.5},
    {"revenu": -1, "ratio_endettement": 28, "incidents": 1},
    {"revenu": 3200, "ratio_endettement": 101, "incidents": 1},
    {"revenu": 1e12, "ratio_endettement": 28, "incidents": 1},
    {"revenu": 3200, "ratio_endettement": 28, "incidents": 9999},
])
def test_demo_web_refuse_le_hors_domaine(corps):
    assert api.post("/api/step/paillier", json=corps).status_code == 422


def test_demo_web_fonctionne_toujours():
    rep = api.post("/api/compare", json={"revenu": 3200, "ratio_endettement": 28, "incidents": 1})
    assert rep.status_code == 200
    data = rep.json()
    assert data["paillier"]["resultat"] == 18.3
    assert abs(data["ckks"]["resultat"] - 18.3) < 1e-3
