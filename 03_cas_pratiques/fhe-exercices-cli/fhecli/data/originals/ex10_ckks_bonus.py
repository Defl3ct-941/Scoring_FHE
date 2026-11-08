"""
Ex10 (bonus) : votre premier calcul FHE réel avec CKKS (TenSEAL)
=================================================================

Paillier n'additionne que des entiers. Pour un vrai score à base de nombres
réels (revenus, ratios, poids décimaux), on utilise CKKS, le schéma de la
bibliothèque TenSEAL (wrapper de Microsoft SEAL). CKKS chiffre des vecteurs de
réels et sait, sur les chiffrés, additionner, multiplier et faire des produits
scalaires. C'est le même schéma que la démo web du projet (04_demo).

TenSEAL est installé automatiquement avec fhe-cli (et embarqué dans les
exécutables). Seule exception : il n'existe pas encore pour Python 3.15, les Mac Intel
ni macOS 13 et antérieur ; les tests de cet exercice y sont alors ignorés.

make_context() est fourni (mêmes paramètres que la démo). Vous implémentez le
produit scalaire chiffré.

À implémenter :
    - encrypted_dot_product(context, values, weights) -> float
        1. Chiffrer values dans un vecteur CKKS :  ts.ckks_vector(context, values)
        2. Produit scalaire avec les poids CLAIRS :  enc_vector.dot(weights)
        3. Déchiffrer et renvoyer le premier élément :  .decrypt()[0]

Ce que ça démontre : le serveur calcule une combinaison pondérée des données
du client sans jamais les voir en clair. CKKS étant approximatif, le résultat
est très proche de la valeur attendue, pas exactement égal (d'où le abs(...) <
1e-3 dans les tests).

Testez avec : fhecli run ex10_ckks_bonus
"""

# I AM NOT DONE

try:
    import tenseal as ts
except ImportError:  # TenSEAL indisponible (Python 3.15, Mac Intel ou macOS < 14) : exercice ignoré
    ts = None


def make_context():
    """Fourni : contexte CKKS prêt à l'emploi (mêmes paramètres que la démo)."""
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60],
    )
    context.generate_galois_keys()
    context.global_scale = 2 ** 40
    return context


def encrypted_dot_product(context, values, weights):
    """Chiffre `values`, calcule le produit scalaire chiffré avec `weights`, déchiffre."""
    # TODO: implémentez les 3 étapes décrites dans l'énoncé
    raise NotImplementedError


# ---------------------------------------------------------------------------
# Tests : ne modifiez pas cette section, elle valide votre implémentation.
# ---------------------------------------------------------------------------

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
