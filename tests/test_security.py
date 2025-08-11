import os
import sys
from pathlib import Path

# Ensure the application package is importable when tests are run directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import security

os.environ["MINIPASS_SECRET_KEY"] = security.base64.urlsafe_b64encode(b"0" * 32).decode()


def test_hash_and_verify():
    pw = "secret"
    hashed = security.hash_password(pw)
    assert security.verify_password(pw, hashed)


def test_encrypt_decrypt():
    text = "hello"
    token = security.encrypt_text(text)
    assert security.decrypt_text(token) == text
