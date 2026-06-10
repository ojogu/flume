import hashlib

from cryptography.fernet import Fernet

from src.utils.config import config
from src.utils.log import get_logger

logger = get_logger(__name__)


def hash_str(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def verify_str(value: str, hashed: str) -> bool:
    return hash_str(value) == hashed


def encryption_key():
    return Fernet(config.encryption_key)


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
