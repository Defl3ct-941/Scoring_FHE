import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exercise import encrypted_dot_product, make_context


def test_matches_plaintext_dot_product():
    context = make_context()
    values = [1500.0, 30.0, 1.0]
    weights = [0.005, -0.9, -10.0]

    result = encrypted_dot_product(context, values, weights)
    expected = sum(v * w for v, w in zip(values, weights))
    assert abs(result - expected) < 1e-3


def test_matches_plaintext_dot_product_other_values():
    context = make_context()
    values = [-1500.0, 55.0, 4.0]
    weights = [0.005, -0.9, -10.0]

    result = encrypted_dot_product(context, values, weights)
    expected = sum(v * w for v, w in zip(values, weights))
    assert abs(result - expected) < 1e-3
