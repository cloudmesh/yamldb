import pytest
import os
from yamldb.YamlDB import YamlDB
from cryptography.fernet import InvalidToken

@pytest.fixture
def enc_file(tmp_path):
    """Provides a temporary file path for the encrypted database."""
    return str(tmp_path / "secrets.enc")

def test_encryption_basic_roundtrip(enc_file):
    """Test that data can be saved and loaded with the correct password."""
    password = "strong-password-123"
    data = {
        "cluster": {
            "admin_token": "secret-token-abc",
            "api_key": "key-xyz-789"
        },
        "global": {"env": "production"}
    }
    
    # Create and save
    db = YamlDB(data=data, filename=enc_file, backend=":encrypt:", password=password)
    
    # Load in a new instance
    db2 = YamlDB(filename=enc_file, backend=":encrypt:", password=password)
    
    assert db2["cluster.admin_token"] == "secret-token-abc"
    assert db2["cluster.api_key"] == "key-xyz-789"
    assert db2["global.env"] == "production"

def test_encryption_wrong_password(enc_file):
    """Test that an incorrect password raises an error during loading."""
    password = "correct-password"
    wrong_password = "wrong-password"
    data = {"secret": "hidden-value"}
    
    # Save with correct password
    db = YamlDB(data=data, filename=enc_file, backend=":encrypt:", password=password)
    
    # Attempt to load with wrong password
    with pytest.raises((InvalidToken, ValueError)):
        YamlDB(filename=enc_file, backend=":encrypt:", password=wrong_password)

def test_encryption_no_password(enc_file):
    """Test that using :encrypt: without a password raises a ValueError."""
    with pytest.raises(ValueError, match="password is required for :encrypt: backend"):
        YamlDB(filename=enc_file, backend=":encrypt:")

def test_encryption_file_is_binary(enc_file):
    """Verify that the file on disk is not plain text YAML."""
    password = "password"
    data = {"key": "value"}
    db = YamlDB(data=data, filename=enc_file, backend=":encrypt:", password=password)
    
    with open(enc_file, "rb") as f:
        content = f.read()
        # The content should not contain the plain text key or value
        assert b"key" not in content
        assert b"value" not in content
        # It should be binary data
        assert len(content) > 0

def test_encryption_update_and_save(enc_file):
    """Test that updating an encrypted DB and saving works correctly."""
    password = "password"
    db = YamlDB(filename=enc_file, backend=":encrypt:", password=password)
    db.set("cluster.status", "secure")
    
    # Reload to verify
    db2 = YamlDB(filename=enc_file, backend=":encrypt:", password=password)
    assert db2["cluster.status"] == "secure"