import pytest
from yamldb.YamlDB import YamlDB

@pytest.fixture
def temp_db_file(tmp_path):
    """Provides a temporary file path for the database."""
    return str(tmp_path / "test_casting_db.yml")

def test_set_with_cast(temp_db_file):
    """Test that set() correctly casts values before storing."""
    db = YamlDB(filename=temp_db_file)
    
    # Cast string to int
    db.set("user.age", "30", cast=int)
    assert db["user.age"] == 30
    assert isinstance(db["user.age"], int)
    
    # Cast string to float
    db.set("settings.pi", "3.14", cast=float)
    assert db["settings.pi"] == 3.14
    assert isinstance(db["settings.pi"], float)
    
    # Test casting failure
    with pytest.raises(ValueError, match="Could not cast value"):
        db.set("user.name", "not_a_number", cast=int)

def test_get_as(temp_db_file):
    """Test that get_as() correctly casts values during retrieval."""
    db = YamlDB(filename=temp_db_file)
    
    # Store as string, retrieve as int
    db["user.age"] = "30"
    assert db.get_as("user.age", int) == 30
    assert isinstance(db.get_as("user.age", int), int)
    
    # Store as string, retrieve as float
    db["settings.timeout"] = "1.5"
    assert db.get_as("settings.timeout", float) == 1.5
    assert isinstance(db.get_as("settings.timeout", float), float)
    
    # Test casting failure returns default
    db["user.name"] = "Gregor"
    assert db.get_as("user.name", int, default=0) == 0
    
    # Test missing key returns default
    assert db.get_as("nonexistent", int, default=-1) == -1

def test_casting_nested_keys(temp_db_file):
    """Test that casting works correctly with nested dot-notation keys."""
    db = YamlDB(filename=temp_db_file)
    
    db.set("a.b.c", "100", cast=int)
    assert db["a.b.c"] == 100
    
    db["a.b.d"] = "200"
    assert db.get_as("a.b.d", int) == 200

def test_smart_boolean_still_works(temp_db_file):
    """Ensure that the existing smart boolean detection still works."""
    db = YamlDB(filename=temp_db_file)
    
    db["settings.enabled"] = "true"
    assert db["settings.enabled"] is True
    
    db["settings.disabled"] = "false"
    assert db["settings.disabled"] is False