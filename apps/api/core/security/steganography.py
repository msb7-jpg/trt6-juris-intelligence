"""LSB image steganography module for hiding encrypted payloads inside PNG images."""

import hashlib
import io
import struct

import numpy as np
from PIL import Image

MAGIC_HEADER = b"JTCU"
HEADER_FORMAT = ">4sI32s"  # magic (4B) + payload_len (4B) + sha256 (32B)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def _bytes_to_bits(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    return np.unpackbits(arr)


def _bits_to_bytes(bits: np.ndarray) -> bytes:
    return np.packbits(bits).tobytes()


def create_cover_png(width: int = 256, height: int = 256) -> bytes:
    """Generate a clean synthetic PNG cover image when the user does not upload one."""
    x = np.linspace(0, 255, width, dtype=np.uint8)
    y = np.linspace(0, 255, height, dtype=np.uint8)
    xv, yv = np.meshgrid(x, y)
    r = ((xv.astype(np.uint16) + yv.astype(np.uint16)) // 2).astype(np.uint8)
    g = np.clip(255 - xv // 2, 0, 255).astype(np.uint8)
    b = np.clip(yv, 0, 255).astype(np.uint8)
    rgb = np.stack([r, g, b], axis=-1)
    img = Image.fromarray(rgb, mode="RGB")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def embed_payload_in_png(image_bytes: bytes, payload: bytes) -> dict:
    """Embed arbitrary bytes (typically encrypted JSON/ciphertext) into PNG LSBs."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pixels = np.array(img, dtype=np.uint8)
    flat = pixels.reshape(-1)

    digest = hashlib.sha256(payload).digest()
    header = struct.pack(HEADER_FORMAT, MAGIC_HEADER, len(payload), digest)
    full_blob = header + payload
    bits = _bytes_to_bits(full_blob)

    capacity_bits = flat.size
    if bits.size > capacity_bits:
        raise ValueError(
            f"Image too small: needs {bits.size} bits, capacity is {capacity_bits} bits."
        )

    modified = flat.copy()
    modified[: bits.size] = (modified[: bits.size] & 0xFE) | bits
    out_pixels = modified.reshape(pixels.shape)

    out_buf = io.BytesIO()
    Image.fromarray(out_pixels, mode="RGB").save(out_buf, format="PNG")
    stego_bytes = out_buf.getvalue()

    return {
        "stego_png_bytes": stego_bytes,
        "stego_sha256": hashlib.sha256(stego_bytes).hexdigest(),
        "payload_sha256": digest.hex(),
        "payload_size_bytes": len(payload),
        "capacity_used_pct": round((bits.size / capacity_bits) * 100, 3),
        "image_dimensions": [img.width, img.height],
    }


def extract_payload_from_png(stego_image_bytes: bytes) -> dict:
    """Extract and verify a hidden payload from a stego PNG image."""
    img = Image.open(io.BytesIO(stego_image_bytes)).convert("RGB")
    flat = np.array(img, dtype=np.uint8).reshape(-1)

    header_bit_count = HEADER_SIZE * 8
    if flat.size < header_bit_count:
        raise ValueError("Image does not contain a valid steganographic header.")

    header_bits = flat[:header_bit_count] & 1
    header_bytes = _bits_to_bytes(header_bits)
    magic, payload_len, expected_digest = struct.unpack(HEADER_FORMAT, header_bytes)

    if magic != MAGIC_HEADER:
        raise ValueError("No hidden payload found (invalid magic header).")

    total_bits = (HEADER_SIZE + payload_len) * 8
    if flat.size < total_bits:
        raise ValueError("Truncated steganographic payload.")

    payload_bits = flat[header_bit_count:total_bits] & 1
    payload = _bits_to_bytes(payload_bits)[:payload_len]
    actual_digest = hashlib.sha256(payload).digest()

    if actual_digest != expected_digest:
        raise ValueError("Steganographic integrity check failed: payload was altered.")

    return {
        "payload": payload,
        "payload_sha256": actual_digest.hex(),
        "payload_size_bytes": payload_len,
        "integrity_verified": True,
    }
