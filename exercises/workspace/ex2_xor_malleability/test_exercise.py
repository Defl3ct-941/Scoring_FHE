import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exercise import reveal_xor_of_plaintexts, xor_bytes, xor_decrypt, xor_encrypt


def test_xor_bytes_basic():
    assert xor_bytes(b"\x00\xff", b"\xff\x00") == b"\xff\xff"
    assert xor_bytes(b"AB", b"AB") == b"\x00\x00"


def test_encrypt_decrypt_roundtrip():
    key = b"secret"
    for message in [b"hello world", b"a", b"", b"x" * 50]:
        enc = xor_encrypt(message, key)
        assert xor_decrypt(enc, key) == message


def test_key_is_repeated():
    key = b"ab"
    message = b"1234"
    enc = xor_encrypt(message, key)
    assert enc == xor_bytes(message, b"abab")


def test_two_time_pad_attack():
    key = b"supersecretkey!!"
    p1 = b"TRANSFER 100 EUR"
    p2 = b"TRANSFER 999 EUR"
    c1 = xor_encrypt(p1, key)
    c2 = xor_encrypt(p2, key)

    # sans connaitre `key`, on doit retrouver p1 XOR p2
    revealed = reveal_xor_of_plaintexts(c1, c2)
    assert revealed == xor_bytes(p1, p2)
