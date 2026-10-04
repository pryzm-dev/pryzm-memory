"""AES-256-GCM avec données associées (AAD) liant chaque valeur à son client,
sa table, sa ligne et sa colonne : une valeur recopiée ailleurs ne s'ouvre pas."""
import json
import os

import numpy as np
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .errors import VaultTampered

KEY_LEN = 32
_VERSION = b"\x01"
_NONCE_LEN = 12
_TAG_LEN = 16


def new_key() -> bytes:
    return os.urandom(KEY_LEN)


def aad(user_id: str, table: str, row_id: str, column: str) -> bytes:
    out = bytearray(b"v1")
    for part in (user_id, table, row_id, column):
        raw = str(part).encode("utf-8")
        out += len(raw).to_bytes(4, "big") + raw
    return bytes(out)


def seal(key: bytes, plaintext: bytes, ad: bytes) -> bytes:
    if len(key) != KEY_LEN:
        raise ValueError("clé de 32 octets attendue")
    nonce = os.urandom(_NONCE_LEN)
    return _VERSION + nonce + AESGCM(key).encrypt(nonce, plaintext, ad)


def open_(key: bytes, blob: bytes, ad: bytes) -> bytes:
    raw = bytes(blob)
    if len(raw) < 1 + _NONCE_LEN + _TAG_LEN or raw[:1] != _VERSION:
        raise VaultTampered("format de valeur chiffrée inconnu")
    try:
        return AESGCM(key).decrypt(raw[1:1 + _NONCE_LEN], raw[1 + _NONCE_LEN:], ad)
    except (InvalidTag, ValueError) as exc:
        raise VaultTampered("valeur chiffrée illisible avec cette clé") from exc


def seal_text(key: bytes, text: str, ad: bytes) -> bytes:
    return seal(key, text.encode("utf-8"), ad)


def open_text(key: bytes, blob: bytes, ad: bytes) -> str:
    return open_(key, blob, ad).decode("utf-8")


def seal_json(key: bytes, obj, ad: bytes) -> bytes:
    return seal(key, json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), ad)


def open_json(key: bytes, blob: bytes, ad: bytes):
    return json.loads(open_(key, blob, ad).decode("utf-8"))


def seal_vec(key: bytes, vec, ad: bytes) -> bytes:
    return seal(key, np.asarray(vec, dtype="<f4").tobytes(), ad)


def open_vec(key: bytes, blob: bytes, ad: bytes) -> np.ndarray:
    return np.frombuffer(open_(key, blob, ad), dtype="<f4").astype(np.float32).copy()
