"""Symmetric cryptography module: Dynamic Key Derivation, Custom SPN Block Cipher, and AES-256-GCM."""

import base64
import hashlib
import hmac
import os
from typing import Literal

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

AlgorithmType = Literal["spn", "aes-256-gcm"]

BLOCK_SIZE = 16
SALT_SIZE = 16
PBKDF2_ITERATIONS = 100_000


def _build_sbox() -> tuple[bytes, bytes]:
    """Build a deterministic bijective 256-byte S-Box and its inverse."""
    sbox = list(range(256))
    # Fisher-Yates shuffle seeded deterministically via SHA-256 chain
    seed = hashlib.sha256(b"jurisTCU-sbox-seed-2026").digest()
    for i in range(255, 0, -1):
        seed = hashlib.sha256(seed + i.to_bytes(2, "big")).digest()
        j = int.from_bytes(seed[:4], "big") % (i + 1)
        sbox[i], sbox[j] = sbox[j], sbox[i]

    inv_sbox = [0] * 256
    for idx, val in enumerate(sbox):
        inv_sbox[val] = idx
    return bytes(sbox), bytes(inv_sbox)


_SBOX, _INV_SBOX = _build_sbox()
_PBOX = [(i * 5 + 3) % BLOCK_SIZE for i in range(BLOCK_SIZE)]
_INV_PBOX = [0] * BLOCK_SIZE
for _src, _dst in enumerate(_PBOX):
    _INV_PBOX[_dst] = _src


def derive_dynamic_key(
    secret: str,
    salt: bytes | None = None,
    nonce: bytes | None = None,
    key_len: int = 32,
) -> tuple[bytes, bytes, bytes]:
    """Derive a dynamic session key using PBKDF2-HMAC-SHA256 with random salt and nonce."""
    used_salt = salt if salt is not None else os.urandom(SALT_SIZE)
    used_nonce = nonce if nonce is not None else os.urandom(8)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_len,
        salt=used_salt + used_nonce,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(secret.encode("utf-8")), used_salt, used_nonce


def _pkcs7_pad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def _pkcs7_unpad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("Invalid padded block length.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size or data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid padding or wrong key.")
    return data[:-pad_len]


def _xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b, strict=True))


def _diffuse_block(block: list[int]) -> list[int]:
    """Cross-byte linear diffusion pass (invertible via _undiffuse_block)."""
    out = list(block)
    for i in range(BLOCK_SIZE):
        nxt = (i + 1) % BLOCK_SIZE
        out[i] = (out[i] ^ ((out[nxt] << 1 | out[nxt] >> 7) & 0xFF)) & 0xFF
    return out


def _undiffuse_block(block: list[int]) -> list[int]:
    out = list(block)
    for i in range(BLOCK_SIZE - 1, -1, -1):
        nxt = (i + 1) % BLOCK_SIZE
        out[i] = (out[i] ^ ((out[nxt] << 1 | out[nxt] >> 7) & 0xFF)) & 0xFF
    return out


class DynamicSPNCipher:
    """128-bit Substitution-Permutation Network (SPN) block cipher in CBC mode."""

    def __init__(self, key: bytes, rounds: int = 8) -> None:
        if len(key) < 16:
            raise ValueError("Key must be at least 16 bytes.")
        self.rounds = max(2, rounds)
        self.round_keys = [
            hmac.new(key, f"round-{r}".encode(), hashlib.sha256).digest()[:BLOCK_SIZE]
            for r in range(self.rounds + 1)
        ]

    def _encrypt_block(self, block: bytes) -> bytes:
        state = list(block)
        for r in range(self.rounds):
            # 1. Key Mixing (XOR)
            rk = self.round_keys[r]
            state = [state[i] ^ rk[i] for i in range(BLOCK_SIZE)]
            # 2. Substitution (S-Box)
            state = [_SBOX[b] for b in state]
            # 3. Permutation (P-Box)
            state = [state[_INV_PBOX[i]] for i in range(BLOCK_SIZE)]
            # 4. Diffusion
            state = _diffuse_block(state)
        final_rk = self.round_keys[self.rounds]
        return bytes(state[i] ^ final_rk[i] for i in range(BLOCK_SIZE))

    def _decrypt_block(self, block: bytes) -> bytes:
        final_rk = self.round_keys[self.rounds]
        state = [block[i] ^ final_rk[i] for i in range(BLOCK_SIZE)]
        for r in range(self.rounds - 1, -1, -1):
            state = _undiffuse_block(state)
            state = [state[_PBOX[i]] for i in range(BLOCK_SIZE)]
            state = [_INV_SBOX[b] for b in state]
            rk = self.round_keys[r]
            state = [state[i] ^ rk[i] for i in range(BLOCK_SIZE)]
        return bytes(state)

    def encrypt(self, plaintext: bytes, iv: bytes | None = None) -> tuple[bytes, bytes]:
        used_iv = iv if iv is not None else os.urandom(BLOCK_SIZE)
        padded = _pkcs7_pad(plaintext)
        blocks: list[bytes] = []
        prev = used_iv
        for offset in range(0, len(padded), BLOCK_SIZE):
            chunk = _xor_bytes(padded[offset : offset + BLOCK_SIZE], prev)
            cipher_block = self._encrypt_block(chunk)
            blocks.append(cipher_block)
            prev = cipher_block
        return b"".join(blocks), used_iv

    def decrypt(self, ciphertext: bytes, iv: bytes) -> bytes:
        if not ciphertext or len(ciphertext) % BLOCK_SIZE != 0:
            raise ValueError("Invalid ciphertext block length.")
        blocks: list[bytes] = []
        prev = iv
        for offset in range(0, len(ciphertext), BLOCK_SIZE):
            cipher_block = ciphertext[offset : offset + BLOCK_SIZE]
            decrypted = self._decrypt_block(cipher_block)
            blocks.append(_xor_bytes(decrypted, prev))
            prev = cipher_block
        return _pkcs7_unpad(b"".join(blocks))


def encrypt_data(
    plaintext: str | bytes,
    secret: str,
    algorithm: AlgorithmType = "spn",
    rounds: int = 8,
) -> dict:
    """Encrypt data with a dynamically derived key using SPN or AES-256-GCM."""
    raw = plaintext.encode("utf-8") if isinstance(plaintext, str) else plaintext
    key, salt, nonce = derive_dynamic_key(secret)
    plaintext_sha256 = hashlib.sha256(raw).hexdigest()

    if algorithm == "aes-256-gcm":
        iv = os.urandom(12)
        ciphertext = AESGCM(key).encrypt(iv, raw, None)
    elif algorithm == "spn":
        ciphertext, iv = DynamicSPNCipher(key, rounds=rounds).encrypt(raw)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    return {
        "algorithm": algorithm,
        "rounds": rounds if algorithm == "spn" else None,
        "ciphertext_b64": base64.b64encode(ciphertext).decode("ascii"),
        "salt_b64": base64.b64encode(salt).decode("ascii"),
        "nonce_b64": base64.b64encode(nonce).decode("ascii"),
        "iv_b64": base64.b64encode(iv).decode("ascii"),
        "plaintext_sha256": plaintext_sha256,
        "ciphertext_sha256": hashlib.sha256(ciphertext).hexdigest(),
        "key_fingerprint": hashlib.sha256(key).hexdigest()[:16],
    }


def decrypt_data(payload: dict, secret: str) -> bytes:
    """Decrypt a payload produced by `encrypt_data` and verify SHA-256 integrity."""
    algorithm = payload["algorithm"]
    ciphertext = base64.b64decode(payload["ciphertext_b64"])
    salt = base64.b64decode(payload["salt_b64"])
    nonce = base64.b64decode(payload["nonce_b64"])
    iv = base64.b64decode(payload["iv_b64"])

    key, _, _ = derive_dynamic_key(secret, salt=salt, nonce=nonce)

    if algorithm == "aes-256-gcm":
        plaintext = AESGCM(key).decrypt(iv, ciphertext, None)
    elif algorithm == "spn":
        rounds = int(payload.get("rounds") or 8)
        plaintext = DynamicSPNCipher(key, rounds=rounds).decrypt(ciphertext, iv)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    expected_hash = payload.get("plaintext_sha256")
    if expected_hash and hashlib.sha256(plaintext).hexdigest() != expected_hash:
        raise ValueError("Integrity check failed: SHA-256 mismatch after decryption.")

    return plaintext
