import tenseal as ts


def make_context() -> ts.Context:
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60],
    )
    context.generate_galois_keys()
    context.global_scale = 2 ** 40
    return context


def encrypted_dot_product(context: ts.Context, values: list[float], weights: list[float]) -> float:
    enc_vector = ts.ckks_vector(context, values)
    enc_result = enc_vector.dot(weights)
    return enc_result.decrypt()[0]
