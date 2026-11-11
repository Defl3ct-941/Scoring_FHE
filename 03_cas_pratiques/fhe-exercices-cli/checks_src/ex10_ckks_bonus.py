"""Vérifications de ex10_ckks_bonus (non distribuées en clair)."""

import pytest


def test_matches_plaintext_dot_product():
    pytest.importorskip("tenseal", reason="TenSEAL indisponible sur cette plateforme (Python 3.15, Mac Intel ou macOS < 14)")
    context = make_context()
    values = [1500.0, 30.0, 1.0]
    weights = [0.005, -0.9, -10.0]

    result = encrypted_dot_product(context, values, weights)
    expected = sum(v * w for v, w in zip(values, weights))
    assert abs(result - expected) < 1e-3


def test_matches_plaintext_dot_product_other_values():
    pytest.importorskip("tenseal", reason="TenSEAL indisponible sur cette plateforme (Python 3.15, Mac Intel ou macOS < 14)")
    context = make_context()
    values = [-1500.0, 55.0, 4.0]
    weights = [0.005, -0.9, -10.0]

    result = encrypted_dot_product(context, values, weights)
    expected = sum(v * w for v, w in zip(values, weights))
    assert abs(result - expected) < 1e-3
