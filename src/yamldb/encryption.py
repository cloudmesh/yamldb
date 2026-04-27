"""
Encryption handler for YamlDB.
Provides secure storage using AES-128 symmetric encryption via the cryptography library.
"""

import os
import base64
from typing import Tuple

class YamlDBEncryption:
    """Handles encryption and decryption of YamlDB data."""

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """Derives a 32-byte key from a password and salt using PBKDF2."""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            from cryptography.hazmat.backends import default_backend
        except ImportError:
            raise ImportError(
                "The 'cryptography' library is required for the :encrypt: backend. "
                "Please install it using: pip install 'yamldb[encrypt]'"
            )
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return base64.b64encode(kdf.derive(password.encode()))

    @classmethod
    def encrypt(cls, data: bytes, password: str) -> bytes:
        """
        Encrypts data and prepends a random 16-byte salt.
        
        Args:
            data (bytes): The raw data to encrypt.
            password (str): The password used for key derivation.
            
        Returns:
            bytes: The salt concatenated with the ciphertext.
        """
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            raise ImportError(
                "The 'cryptography' library is required for the :encrypt: backend. "
                "Please install it using: pip install 'yamldb[encrypt]'"
            )

        salt = os.urandom(16)
        key = cls._derive_key(password, salt)
        f = Fernet(key)
        ciphertext = f.encrypt(data)
        return salt + ciphertext

    @classmethod
    def decrypt(cls, encrypted_data: bytes, password: str) -> bytes:
        """
        Decrypts data using the salt prepended to the ciphertext.
        
        Args:
            encrypted_data (bytes): The salt + ciphertext.
            password (str): The password used for key derivation.
            
        Returns:
            bytes: The decrypted raw data.
        """
        if len(encrypted_data) < 16:
            raise ValueError("Encrypted data is too short to contain a salt.")

        try:
            from cryptography.fernet import Fernet
        except ImportError:
            raise ImportError(
                "The 'cryptography' library is required for the :encrypt: backend. "
                "Please install it using: pip install 'yamldb[encrypt]'"
            )

        salt = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        key = cls._derive_key(password, salt)
        f = Fernet(key)
        return f.decrypt(ciphertext)