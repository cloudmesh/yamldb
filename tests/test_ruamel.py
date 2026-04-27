import pytest
from pathlib import Path
from yamldb.YamlDB import YamlDB

@pytest.fixture
def temp_db_file(tmp_path):
    """Provides a temporary file path for the database."""
    return str(tmp_path / "test_ruamel_db.yml")

def test_comment_preservation(temp_db_file):
    """Test that comments are preserved after loading, modifying, and saving."""
    yaml_content = """# Database Configuration
user:
  name: Gregor # The primary user
  age: 30 # Age in years
# System settings
settings:
  theme: dark
"""
    with open(temp_db_file, "w") as f:
        f.write(yaml_content)

    db = YamlDB(filename=temp_db_file)
    
    # Modify a value
    db["user.age"] = 31
    db.save()

    # Read the file back as raw text to check for comments
    with open(temp_db_file, "r") as f:
        content = f.read()

    assert "# Database Configuration" in content
    assert "# The primary user" in content
    assert "# Age in years" in content
    assert "# System settings" in content
    assert "age: 31" in content

def test_exception_handling_contains(temp_db_file):
    """Test that __contains__ handles missing keys correctly."""
    db = YamlDB(filename=temp_db_file)
    db["a.b"] = 1
    
    assert "a.b" in db
    assert "a.c" not in db
    assert "x.y" not in db

def test_exception_handling_set_types(temp_db_file):
    """Test that set() handles non-string values for boolean conversion safely."""
    db = YamlDB(filename=temp_db_file)
    
    # Should not raise AttributeError when value is not a string
    db["test.val"] = 123
    assert db["test.val"] == 123
    
    db["test.val"] = None
    assert db["test.val"] is None

def test_exception_handling_getitem_errors(temp_db_file):
    """Test that __getitem__ raises appropriate errors."""
    db = YamlDB(filename=temp_db_file)
    db["a"] = 1
    
    with pytest.raises(KeyError):
        _ = db["nonexistent"]
    
    with pytest.raises(ValueError):
        # Try to access a nested key on a non-dict value
        _ = db["a.b"]

def test_exception_handling_delete_errors(temp_db_file):
    """Test that delete() handles missing keys without crashing."""
    db = YamlDB(filename=temp_db_file)
    db["a.b"] = 1
    
    # Deleting non-existent key should not raise exception (based on current implementation)
    db.delete("nonexistent")
    db.delete("a.c")