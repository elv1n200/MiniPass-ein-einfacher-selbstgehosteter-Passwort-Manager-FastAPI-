import base64
import os

import bcrypt
from cryptography.fernet import Fernet


def _get_key() -> bytes:
    """Return the Fernet key from environment variable.

    The key must be a 32 url-safe base64-encoded bytes. If the provided
    environment variable is not encoded, it will be adjusted accordingly.
    """
    raw = os.environ.get("MINIPASS_SECRET_KEY")
    if not raw:
        raise RuntimeError("MINIPASS_SECRET_KEY environment variable not set")
    try:
        # try to use as given
        base64.urlsafe_b64decode(raw)
        return raw.encode()
    except Exception:
        # pad/trim and encode
        return base64.urlsafe_b64encode(raw.encode().ljust(32)[:32])


def _fernet() -> Fernet:
    return Fernet(_get_key())


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def encrypt_text(text: str) -> bytes:
    f = _fernet()
    return f.encrypt(text.encode())


def decrypt_text(token: bytes) -> str:
    f = _fernet()
    return f.decrypt(token).decode()
