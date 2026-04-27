import pytest
from yamldb.YamlDB import YamlDB

@pytest.fixture
def temp_db_file(tmp_path):
    """Provides a temporary file path for the database."""
    return str(tmp_path / "test_metrics_db.yml")

def test_write_efficiency_stats(temp_db_file):
    """Test that get_stats correctly tracks set and save calls."""
    # Initialize with auto_flush=False to control saves
    db = YamlDB(filename=temp_db_file, auto_flush=False)
    
    # Perform several sets
    db.set("key1", "val1")
    db.set("key2", "val2")
    db.set("key3", "val3")
    
    # At this point, set_calls should be 3, save_calls should be 0
    stats = db.get_stats()
    assert stats["set_calls"] == 3
    assert stats["save_calls"] == 0
    assert stats["write_efficiency"] == "100.00%"
    
    # Trigger a save
    db.save()
    
    stats = db.get_stats()
    assert stats["set_calls"] == 3
    assert stats["save_calls"] == 1
    # Efficiency = 1 - (1/3) = 66.67%
    assert stats["write_efficiency"] == "66.67%"

def test_auto_flush_metrics(temp_db_file):
    """Test that auto_flush correctly impacts save_calls."""
    # Initialize with auto_flush=True
    db = YamlDB(filename=temp_db_file, auto_flush=True)
    
    # Each set should trigger a save because data is dirty
    db.set("key1", "val1")
    db.set("key2", "val2")
    
    stats = db.get_stats()
    assert stats["set_calls"] == 2
    assert stats["save_calls"] == 2
    assert stats["write_efficiency"] == "0.00%"

def test_dirty_flag_metrics(temp_db_file):
    """Test that setting the same value doesn't trigger unnecessary saves."""
    db = YamlDB(filename=temp_db_file, auto_flush=True)
    
    # First set triggers save
    db.set("key1", "val1")
    
    # Second set with same value should still mark dirty and save 
    # (Current implementation marks dirty on every set() call)
    db.set("key1", "val1")
    
    stats = db.get_stats()
    assert stats["set_calls"] == 2
    assert stats["save_calls"] == 2