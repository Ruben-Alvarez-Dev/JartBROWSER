"""Encryption service for secure API key storage"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from typing import Optional


class EncryptionService:
    """Service for encrypting/decrypting sensitive data"""

    def __init__(self, key: Optional[str] = None):
        if key:
            self.fernet = Fernet(key.encode())
        else:
            # Generate a new key if not provided
            self.fernet = self._generate_key()

    def _generate_key(self) -> Fernet:
        """Generate a new encryption key"""
        # In production, this should come from environment or key management
        password = os.urandom(32)
        salt = os.urandom(16)
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a string"""
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a string"""
        return self.fernet.decrypt(ciphertext.encode()).decode()

    @staticmethod
    def generate_key_string() -> str:
        """Generate a new key as a string"""
        return Fernet.generate_key().decode()


# Global instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create the global encryption service"""
    global _encryption_service
    if _encryption_service is None:
        key = os.environ.get("JARTBROWSER_ENCRYPTION_KEY")
        _encryption_service = EncryptionService(key)
    return _encryption_service
