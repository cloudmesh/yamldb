import pytest
from pathlib import Path
from yamldb.YamlDB import YamlDB

@pytest.fixture
def temp_db_file(tmp_path):
    """Provides a temporary file path for the database."""
    return str(tmp_path / "test_db.yml")

@pytest.fixture
def db(temp_db_file):
    """Provides a YamlDB instance using a temporary file."""
    return YamlDB(filename=temp_db_file)

def test_basic_set_get(db):
    """Test basic set and get operations."""
    db["name"] = "Gregor"
    assert db["name"] == "Gregor"
    assert db.get("name") == "Gregor"

def test_dot_notation_set_get(db):
    """Test nested keys using dot notation."""
    db["user.profile.name"] = "Gregor"
    assert db["user.profile.name"] == "Gregor"
    assert db.data["user"]["profile"]["name"] == "Gregor"

def test_len_fix(db):
    """Test that __len__ returns the correct number of top-level keys."""
    db["a"] = 1
    db["b"] = 2
    db["c.d"] = 3  # This is one top-level key 'c'
    assert len(db) == 3

def test_get_default_no_mutation(db):
    """Test that get() with a default does not mutate the database."""
    key = "nonexistent.key"
    default_val = "default"
    
    assert db.get(key, default=default_val) == default_val
    assert key not in db
    assert len(db) == 0

def test_yaml_output(db):
    """Test that yaml() returns a valid YAML string."""
    db["a"] = 1
    db["b"] = {"c": 2}
    yaml_out = db.yaml()
    assert "a: 1" in yaml_out
    assert "b:" in yaml_out
    assert "c: 2" in yaml_out

def test_pathlib_dir_creation(tmp_path):
    """Test that YamlDB creates parent directories if they don't exist."""
    nested_dir = tmp_path / "subdir" / "another_dir"
    filename = str(nested_dir / "db.yml")
    
    # This should not raise an exception
    db = YamlDB(filename=filename)
    assert Path(filename).exists()
    assert nested_dir.exists()

def test_persistence(temp_db_file):
    """Test that data is persisted to disk and can be reloaded."""
    db1 = YamlDB(filename=temp_db_file)
    db1["persist.test"] = "saved"
    db1.save()
    
    db2 = YamlDB(filename=temp_db_file)
    assert db2["persist.test"] == "saved"

def test_search_jmespath(db):
    """Test JMESPath search functionality."""
    db["users"] = [
        {"name": "Gregor", "age": 100},
        {"name": "Alice", "age": 200},
    ]
    
    # Search for users with age > 150
    result = db.search("users[?age > `150`].name")
    assert result == ["Alice"]

def test_delete_nested(db):
    """Test deleting nested keys."""
    db["a.b.c"] = 1
    db["a.b.d"] = 2
    
    db.delete("a.b.c")
    assert "a.b.c" not in db
    assert db["a.b.d"] == 2