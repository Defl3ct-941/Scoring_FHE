"""Vérifications de ex3_fernet_tamper (non distribuées en clair)."""

import pytest


def test_roundtrip():
    key = Fernet.generate_key()
    token = encrypt_value("hello bank", key)
    assert isinstance(token, bytes)
    assert decrypt_value(token, key) == "hello bank"


def test_different_keys_cannot_decrypt():
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()
    token = encrypt_value("secret data", key1)
    with pytest.raises(Exception):
        decrypt_value(token, key2)


def test_tampering_is_detected():
    key = Fernet.generate_key()
    token = encrypt_value("revenu=4000", key)
    assert tamper_and_check(token, key) is True
