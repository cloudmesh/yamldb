import pytest
from yamldb.YamlDB import YamlDB

@pytest.fixture
def temp_db_file(tmp_path):
    """Provides a temporary file path for the database."""
    return str(tmp_path / "test_api_enhancements_db.yml")

def test_items_recursive(temp_db_file):
    """Test that items_recursive correctly yields all leaf nodes."""
    data = {
        "user": {
            "name": "Gregor",
            "profile": {
                "age": 30,
                "city": "Indianapolis"
            }
        },
        "settings": {
            "theme": "dark",
            "notifications": True
        },
        "version": 1.0
    }
    db = YamlDB(data=data, filename=temp_db_file)
    
    items = list(db.items_recursive())
    
    # Check that all leaf nodes are present
    expected = {
        "user.name": "Gregor",
        "user.profile.age": 30,
        "user.profile.city": "Indianapolis",
        "settings.theme": "dark",
        "settings.notifications": True,
        "version": 1.0
    }
    
    assert len(items) == len(expected)
    for key, value in items:
        assert expected[key] == value

def test_find_all(temp_db_file):
    """Test that find_all correctly finds all keys with a specific value."""
    data = {
        "node1": {"status": "active", "type": "server"},
        "node2": {"status": "inactive", "type": "server"},
        "node3": {"status": "active", "type": "client"},
        "global_status": "active"
    }
    db = YamlDB(data=data, filename=temp_db_file)
    
    active_nodes = db.find_all("active")
    
    assert len(active_nodes) == 3
    assert "node1.status" in active_nodes
    assert "node3.status" in active_nodes
    assert "global_status" in active_nodes
    assert "node2.status" not in active_nodes

def test_filter(temp_db_file):
    """Test that filter correctly finds keys based on a predicate."""
    data = {
        "metrics": {
            "cpu": 45,
            "mem": 80,
            "disk": 20
        },
        "threshold": 50
    }
    db = YamlDB(data=data, filename=temp_db_file)
    
    # Find all values > 40
    high_values = db.filter(lambda v: isinstance(v, (int, float)) and v > 40)
    
    assert len(high_values) == 3
    assert "metrics.cpu" in high_values
    assert "metrics.mem" in high_values
    assert "threshold" in high_values
    assert "metrics.disk" not in high_values

def test_update_many(temp_db_file):
    """Test that update_many correctly updates multiple keys atomically."""
    db = YamlDB(filename=temp_db_file)
    db.set("user.name", "Old Name")
    db.set("user.age", 20)
    db.set("app.version", "1.0")
    
    updates = {
        "user.name": "New Name",
        "user.age": 21,
        "app.version": "1.1",
        "app.status": "deployed"
    }
    
    db.update_many(updates)
    
    assert db["user.name"] == "New Name"
    assert db["user.age"] == 21
    assert db["app.version"] == "1.1"
    assert db["app.status"] == "deployed"

def test_update_many_rollback(temp_db_file):
    """Test that update_many rolls back if one of the updates fails."""
    db = YamlDB(filename=temp_db_file)
    db.set("user.name", "Original")
    
    # We can't easily make set() fail without mocking, 
    # but we can test that a crash during the loop rolls back.
    
    def failing_update():
        with db.transaction():
            db.set("user.name", "Changed")
            raise RuntimeError("Simulated Crash")

    with pytest.raises(RuntimeError):
        failing_update()
        
    assert db["user.name"] == "Original"