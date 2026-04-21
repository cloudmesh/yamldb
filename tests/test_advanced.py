import pytest
import os
from pathlib import Path
from yamldb import YamlDB

def test_transaction_commit(tmp_path):
    db_file = tmp_path / "test_commit.yml"
    db = YamlDB(filename=str(db_file))
    
    with db.transaction():
        db.set("key1", "value1")
        db.set("key2", "value2")
    
    # Verify changes are persisted
    db2 = YamlDB(filename=str(db_file))
    assert db2.get("key1") == "value1"
    assert db2.get("key2") == "value2"

def test_transaction_rollback(tmp_path):
    db_file = tmp_path / "test_rollback.yml"
    db = YamlDB(filename=str(db_file))
    db.set("initial", "value")
    
    try:
        with db.transaction():
            db.set("initial", "changed")
            db.set("new_key", "new_value")
            raise RuntimeError("Force rollback")
    except RuntimeError:
        pass
    
    # Verify changes are rolled back
    assert db.get("initial") == "value"
    assert db.get("new_key") is None
    
    # Verify file still has original value
    db2 = YamlDB(filename=str(db_file))
    assert db2.get("initial") == "value"
    assert db2.get("new_key") is None

from unittest.mock import patch

def test_concurrency_lock(tmp_path):
    db_file = tmp_path / "test_lock.yml"
    db1 = YamlDB(filename=str(db_file))
    
    # Manually acquire lock to simulate another process
    db1._acquire_lock()
    
    # Try to create another instance without calling load() in __init__
    # to avoid the lock acquisition failure during initialization
    with patch.object(YamlDB, 'load', return_value=None):
        db2 = YamlDB(filename=str(db_file))
    
    with pytest.raises(RuntimeError) as excinfo:
        # Use a very short timeout for the test
        db2._acquire_lock(timeout=0.2)
    
    assert "Timeout acquiring lock" in str(excinfo.value)
    
    # Release lock and try again
    db1._release_lock()
    assert db2._acquire_lock(timeout=0.2) is True
    db2._release_lock()

def test_atomic_write_cleanup(tmp_path):
    db_file = tmp_path / "test_atomic.yml"
    db = YamlDB(filename=str(db_file))
    db.set("key", "value")
    
    # Check that no .tmp files are left behind
    for file in tmp_path.glob("*.tmp"):
        pytest.fail(f"Temporary file {file} was not cleaned up")
    
    # Check that lock file is cleaned up
    lock_file = Path(f"{db_file}.lock")
    assert not lock_file.exists()