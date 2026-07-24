import hashlib
import hmac

from cryptography.fernet import Fernet
import sqlalchemy as sa

from src.utils.config import config
from src.utils.log import get_logger

logger = get_logger(__name__)


# One-way hashing for API keys — we can verify but never recover the raw key
def hash_str(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def verify_str(value: str, hashed: str) -> bool:
    return hash_str(value) == hashed


def build_signed_headers(body_bytes: bytes, secret: str, event_id: str) -> dict:
    """Compute HMAC-SHA256 signature and return the standard webhook delivery headers."""
    signature = hmac.new(secret.encode(), body_bytes, hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-Signature-256": f"sha256={signature}",
        "X-Event-ID": event_id,
        "User-Agent": "Flume-Webhook/1.0",
    }


def encryption_key():
    return Fernet(config.encryption_key)


# Reversible encryption for data we need to read back (OAuth tokens, etc.)
def encrypt_token(token: str) -> str:
    cipher = encryption_key()
    return cipher.encrypt(token.encode()).decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    try:
        cipher = encryption_key()
        return cipher.decrypt(encrypted_token.encode()).decode("utf-8")
    except Exception as e:
        logger.error(f"Error decrypting token: {e}", exc_info=True)
        raise


class EncryptedText(sa.TypeDecorator):
    """Transparently encrypts text at rest, decrypts on read.

    Uses Fernet symmetric encryption via ``encrypt_token`` / ``decrypt_token``.
    The plaintext value is what the application sees; the DB stores the ciphertext.
    """

    impl = sa.Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        if value is not None:
            return encrypt_token(value)
        return value

    def process_result_value(self, value: str | None, dialect) -> str | None:
        if value is not None:
            return decrypt_token(value)
        return value
