"""
Convention d'encodage partagee par le client separe, le serveur et les mesures.

Paillier calcule sur des ENTIERS. Les entrees et les poids sont donc arrondis
au millieme (SCALE = 1000) avant chiffrement. Le produit poids x entree est a
l'echelle SCALE * SCALE, d'ou le biais encode a cette meme echelle.

Consequence a retenir : le calcul homomorphe est exact sur ces entiers, mais
l'arrondi initial peut ecarter le resultat de la formule sur les reels
(`encoded_reference` contre `config.plaintext_score`).
"""

from app import config

SCALE = 1000
RESULT_SCALE = SCALE * SCALE

# Domaine metier accepte par l'API (bornes larges autour des curseurs de la demo).
REVENU_MAX = 100_000.0
RATIO_MAX = 100.0
INCIDENTS_MAX = 50


def encode_features(revenu: float, ratio_endettement: float, incidents: float) -> list[int]:
    x = config.centered_features(revenu, ratio_endettement, incidents)
    return [round(v * SCALE) for v in x]


def encoded_weights() -> list[int]:
    return [round(w * SCALE) for w in config.WEIGHTS_VECTOR]


def encoded_bias() -> int:
    return round(config.BIAS * RESULT_SCALE)


def encoded_reference(revenu: float, ratio_endettement: float, incidents: float) -> float:
    """Score obtenu EN CLAIR avec exactement les entiers que Paillier manipule."""
    xi = encode_features(revenu, ratio_endettement, incidents)
    total = encoded_bias() + sum(w * x for w, x in zip(encoded_weights(), xi))
    return total / RESULT_SCALE


def max_encoded_magnitude() -> int:
    """Majorant de |score encode| sur tout le domaine accepte.

    Le dechiffrement signe n'est correct que si cette valeur reste < n / 2.
    Avec n >= 2048 bits la marge est immense ; le serveur le verifie quand meme.
    """
    bounds = [
        round(max(REVENU_MAX - 2500.0, 2500.0) * SCALE),
        round(RATIO_MAX * SCALE),
        INCIDENTS_MAX * SCALE,
    ]
    return abs(encoded_bias()) + sum(abs(w) * b for w, b in zip(encoded_weights(), bounds))
