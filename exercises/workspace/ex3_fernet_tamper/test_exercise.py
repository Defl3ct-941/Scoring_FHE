import sys
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exercise import decrypt_value, encrypt_value, tamper_and_check


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
