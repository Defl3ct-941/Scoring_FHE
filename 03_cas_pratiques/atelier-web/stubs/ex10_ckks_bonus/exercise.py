"""
Ex10 (Bonus) - Votre premier calcul FHE avec CKKS (TenSEAL).

Voir README.md pour l'enonce complet.
"""

import tenseal as ts


def make_context() -> ts.Context:
    """Fourni : contexte CKKS pret a l'emploi (memes parametres que la demo)."""
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60],
    )
    context.generate_galois_keys()
    context.global_scale = 2 ** 40
    return context


def encrypted_dot_product(context: ts.Context, values: list[float], weights: list[float]) -> float:
    """Chiffre `values`, calcule le produit scalaire chiffre avec `weights`, dechiffre."""
    # TODO: implementez cette fonction (3 lignes, voir le README)
    raise NotImplementedError
