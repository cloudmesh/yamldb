"""
Backend strategies for YamlDB.
Defines how data is loaded from and saved to different storage formats.
"""

import os
import tempfile
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
from ruamel.yaml import YAML
from .encryption import YamlDBEncryption

class BaseBackend(ABC):
    """Abstract base class for all YamlDB backends."""

    @abstractmethod
    def load(self, filename: str) -> Dict[Any, Any]:
        """Load data from the specified file."""
        pass

    @abstractmethod
    def save(self, filename: str, data: Dict[Any, Any]) -> None:
        """Save data to the specified file atomically."""
        pass

    def _atomic_write(self, filename: str, write_func) -> None:
        """
        Helper to perform an atomic write using a temporary file.
        
        Args:
            filename (str): Target filename.
            write_func (Callable): Function that takes a file object and writes data to it.
        """
        path = Path(filename)
        with tempfile.NamedTemporaryFile(
            "wb" if "b" in str(write_func) else "w", 
            dir=path.parent, 
            delete=False, 
            suffix=".tmp"
        ) as tf:
            # The write_func might expect a text file or binary file
            # We handle the mode based on the write_func's needs
            # For simplicity in this implementation, we'll let the specific backend 
            # handle the temp file creation if they need specific modes.
            pass

class FileBackend(BaseBackend):
    """Standard YAML backend using ruamel.yaml for comment preservation."""

    def __init__(self):
        self._yaml = YAML(typ='rt')
        self._yaml.preserve_quotes = True
        self._yaml.indent(mapping=2, sequence=4, offset=2)

    def load(self, filename: str) -> Dict[Any, Any]:
        path = Path(filename)
        if not path.exists():
            return {}
        with open(path, "r") as f:
            return self._yaml.load(f) or {}

    def save(self, filename: str, data: Dict[Any, Any]) -> None:
        path = Path(filename)
        with tempfile.NamedTemporaryFile(
            "w", dir=path.parent, delete=False, suffix=".tmp"
        ) as tf:
            self._yaml.dump(data, tf)
            temp_name = tf.name
        os.replace(temp_name, path)

class BinaryBackend(BaseBackend):
    """High-performance binary backend using JSON serialization."""

    def load(self, filename: str) -> Dict[Any, Any]:
        path = Path(filename)
        if not path.exists():
            return {}
        with open(path, "rb") as f:
            return json.loads(f.read().decode('utf-8')) or {}

    def save(self, filename: str, data: Dict[Any, Any]) -> None:
        path = Path(filename)
        # Convert CommentedMap to plain dict for JSON
        from .YamlDB import YamlDB # Local import to avoid circularity if needed, 
                                   # but we'll use a helper for plain dict conversion
        
        # We need a way to convert ruamel.yaml CommentedMap to plain dict
        # I'll implement a helper method for this.
        plain_data = self._to_plain_dict(data)
        
        with tempfile.NamedTemporaryFile(
            "wb", dir=path.parent, delete=False, suffix=".tmp"
        ) as tf:
            tf.write(json.dumps(plain_data).encode('utf-8'))
            temp_name = tf.name
        os.replace(temp_name, path)

    def _to_plain_dict(self, data: Any) -> Any:
        from collections.abc import MutableMapping
        if isinstance(data, MutableMapping):
            return {str(k): self._to_plain_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._to_plain_dict(i) for i in data]
        return data

class EncryptedBackend(BaseBackend):
    """Secure backend using AES-128 symmetric encryption."""

    def __init__(self, password: str):
        self.password = password

    def load(self, filename: str) -> Dict[Any, Any]:
        path = Path(filename)
        if not path.exists():
            return {}
        with open(path, "rb") as f:
            encrypted_data = f.read()
            if not encrypted_data:
                return {}
            decrypted_data = YamlDBEncryption.decrypt(encrypted_data, self.password)
            return json.loads(decrypted_data.decode('utf-8')) or {}

    def save(self, filename: str, data: Dict[Any, Any]) -> None:
        path = Path(filename)
        # Convert to plain dict for JSON
        plain_data = self._to_plain_dict(data)
        encrypted_data = YamlDBEncryption.encrypt(
            json.dumps(plain_data).encode('utf-8'), 
            self.password
        )
        
        with tempfile.NamedTemporaryFile(
            "wb", dir=path.parent, delete=False, suffix=".tmp"
        ) as tf:
            tf.write(encrypted_data)
            temp_name = tf.name
        os.replace(temp_name, path)

    def _to_plain_dict(self, data: Any) -> Any:
        from collections.abc import MutableMapping
        if isinstance(data, MutableMapping):
            return {str(k): self._to_plain_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._to_plain_dict(i) for i in data]
        return data