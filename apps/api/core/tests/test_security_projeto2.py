"""Unit tests for Projeto 2 security modules: cipher, steganography, attacks, and AI anomalies."""

import pytest

from core.security.attacks import (
    evaluate_security_suite,
    run_brute_force_attack,
    run_differential_attack,
    run_statistical_attack,
)
from core.security.cipher import decrypt_data, derive_dynamic_key, encrypt_data
from core.security.steganography import (
    create_cover_png,
    embed_payload_in_png,
    extract_payload_from_png,
)


def test_dynamic_key_is_never_fixed():
    k1, s1, n1 = derive_dynamic_key("segredo-teste")
    k2, s2, n2 = derive_dynamic_key("segredo-teste")
    assert s1 != s2 or n1 != n2
    assert k1 != k2


@pytest.mark.parametrize("algorithm", ["spn", "aes-256-gcm"])
def test_encrypt_decrypt_roundtrip_and_wrong_key(algorithm: str):
    plaintext = "Acordao TCU 2026 - Informacao sigilosa com acentos e simbolos: R$ 1.250,00!"
    payload = encrypt_data(plaintext, secret="chave-mestra-2026", algorithm=algorithm)

    recovered = decrypt_data(payload, secret="chave-mestra-2026").decode("utf-8")
    assert recovered == plaintext

    with pytest.raises(Exception):
        decrypt_data(payload, secret="chave-errada")


def test_steganography_embed_extract_and_integrity():
    cover = create_cover_png(200, 200)
    secret_payload = b'{"ciphertext":"abc123","alg":"spn"}'
    embedded = embed_payload_in_png(cover, secret_payload)
    assert embedded["payload_size_bytes"] == len(secret_payload)

    extracted = extract_payload_from_png(embedded["stego_png_bytes"])
    assert extracted["integrity_verified"] is True
    assert extracted["payload"] == secret_payload


def test_attacks_avalanche_statistical_and_brute_force():
    plaintext = "Dados experimentais de auditoria para teste de difusao e confusao criptografica."
    secret = "Segredo@2026"

    brute = run_brute_force_attack(plaintext, secret, algorithm="spn", reduced_key_bits=10)
    assert brute["cracked_reduced_key"] is True
    assert brute["viable_against_full_key"] is False

    diff = run_differential_attack(plaintext, secret, algorithm="spn")
    assert diff["avalanche_pct"] > 30.0
    assert diff["has_avalanche_effect"] is True

    stat = run_statistical_attack(plaintext, secret, algorithm="spn")
    assert stat["shannon_entropy"] > 7.0
    assert stat["patterns_detected"] is False

    suite = evaluate_security_suite(plaintext, secret, algorithm="aes-256-gcm")
    assert suite["verdict"]["is_system_secure"] is True
