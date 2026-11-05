import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exercise import encrypted_score, generate_keypair

P, Q = 1009, 1013


def test_matches_plaintext_computation():
    pub, priv = generate_keypair(P, Q)
    features = [4000 - 2500, 30, 1]  # revenu centre, ratio, incidents
    weights = [5, -9, -10]  # poids "en points x 1000" comme dans la demo
    bias = 50

    result = encrypted_score(pub, priv, features, weights, bias)
    expected = bias + sum(w * x for w, x in zip(weights, features))
    assert result == expected


def test_matches_plaintext_computation_other_profile():
    pub, priv = generate_keypair(P, Q)
    features = [1000 - 2500, 55, 4]
    weights = [5, -9, -10]
    bias = 50

    result = encrypted_score(pub, priv, features, weights, bias)
    expected = bias + sum(w * x for w, x in zip(weights, features))
    assert result == expected


def test_handles_negative_final_score():
    pub, priv = generate_keypair(P, Q)
    features = [1000 - 2500, 60, 5]
    weights = [5, -9, -10]
    bias = 50

    result = encrypted_score(pub, priv, features, weights, bias)
    expected = bias + sum(w * x for w, x in zip(weights, features))
    assert expected < 0  # sanity check sur le scenario choisi
    assert result == expected
