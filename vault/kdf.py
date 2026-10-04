"""Dérivations : Argon2id (mot de passe, phrase), HKDF (jetons de session),
enveloppes de la clé de coffre, empreintes et index aveugles."""
import hashlib
import hmac
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from . import crypto
from .errors import VaultTampered, WrongSecret

ARGON2_DEFAULT = {"alg": "argon2id", "t": 3, "m_kib": 65536, "p": 1}
_SALT_LEN = 16


def new_salt() -> bytes:
    return os.urandom(_SALT_LEN)


def argon2id(secret: str, salt: bytes, params: dict = ARGON2_DEFAULT) -> bytes:
    if params.get("alg") != "argon2id":
        raise ValueError("algorithme de dérivation inconnu")
    kdf = Argon2id(salt=bytes(salt), length=32, iterations=int(params["t"]),
                   lanes=int(params["p"]), memory_cost=int(params["m_kib"]))
    return kdf.derive(secret.encode("utf-8"))


def hkdf_session(token: str, salt: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=bytes(salt),
                info=b"pryzm-vault-session-v1").derive(token.encode("utf-8"))


def _label(label: str) -> bytes:
    return b"wrap|" + label.encode("utf-8")


def wrap(kek: bytes, dek: bytes, label: str) -> bytes:
    return crypto.seal(kek, dek, _label(label))


def unwrap(kek: bytes, blob: bytes, label: str) -> bytes:
    try:
        return crypto.open_(kek, blob, _label(label))
    except VaultTampered as exc:
        raise WrongSecret("secret incorrect") from exc


def token_hash(token: str) -> bytes:
    return hashlib.sha256(token.encode("utf-8")).digest()


def _blind_key(dek: bytes) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"pryzm-vault-blind-v1").derive(dek)


def blind(dek: bytes, value: str) -> str:
    mac = hmac.new(_blind_key(dek), value.encode("utf-8"), hashlib.sha256).hexdigest()
    return "b:" + mac[:40]
