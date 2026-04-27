import pytest
from pathlib import Path
from unittest.mock import patch
from yamldb.YamlDB import YamlDB

@pytest.fixture
def temp_db_file(tmp_path):
    """Provides a temporary file path for the database."""
    return str(tmp_path / "perf_test_db.yml")

def test_auto_flush_disabled(temp_db_file):
    """Test that save is not called when auto_flush is False."""
    # Initialize with auto_flush=False
    db = YamlDB(filename=temp_db_file, auto_flush=False)
    
    with patch.object(YamlDB, 'save') as mock_save:
        db["test.key"] = "value"
        # flush() is called inside set(), but it should not call save() because auto_flush is False
        mock_save.assert_not_called()
        
        # Manually calling flush() should also not call save() if auto_flush is False
        db.flush()
        mock_save.assert_not_called()

def test_dirty_flag_optimization(temp_db_file):
    """Test that save is not called if data is not dirty."""
    db = YamlDB(filename=temp_db_file, auto_flush=True)
    
    # First, make it clean
    db._dirty = False
    
    with patch.object(YamlDB, 'save') as mock_save:
        # Calling flush on clean data should not trigger save
        db.flush()
        mock_save.assert_not_called()
        
        # Modifying data should make it dirty and trigger save
        db["test.key"] = "value"
        mock_save.assert_called_once()

def test_transaction_overrides_auto_flush(temp_db_file):
    """Test that transactions handle saving regardless of auto_flush."""
    db = YamlDB(filename=temp_db_file, auto_flush=False)
    
    with patch.object(YamlDB, 'save') as mock_save:
        with db.transaction():
            db["test.key"] = "value"
            # Inside transaction, flush() is called but should not save
            mock_save.assert_not_called()
        
        # After transaction commit, save() should be called once
        mock_save.assert_called_once()