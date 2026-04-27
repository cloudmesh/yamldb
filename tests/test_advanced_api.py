import pytest
from yamldb import YamlDB
from pathlib import Path

def test_count(tmp_path):
    """Test the count() method with JMESPath queries."""
    filename = str(tmp_path / "count_test.yml")
    db = YamlDB(filename=filename)
    db.set("users.user1.status", "active")
    db.set("users.user2.status", "inactive")
    db.set("users.user3.status", "active")
    
    # Count active users
    assert db.count("(users.*)[?status=='active']") == 2
    # Count all users
    assert db.count("users.*") == 3
    # Count non-existent
    assert db.count("(users.*)[?status=='pending']") == 0
    # Count single item
    assert db.count("users.user1") == 1

def test_upsert(tmp_path):
    """Test the upsert() method."""
    filename = str(tmp_path / "upsert_test.yml")
    db = YamlDB(filename=filename)
    
    # Insert new key
    is_new = db.upsert("app.version", "1.0.0")
    assert is_new is True
    assert db.get("app.version") == "1.0.0"
    
    # Update existing key
    is_new = db.upsert("app.version", "1.1.0")
    assert is_new is False
    assert db.get("app.version") == "1.1.0"

def test_merge_dict(tmp_path):
    """Test merging a dictionary into the DB."""
    filename = str(tmp_path / "merge_test.yml")
    db = YamlDB(filename=filename)
    db.set("cluster.name", "prod-cluster")
    db.set("cluster.nodes.node1.cpu", 16)
    
    merge_data = {
        "cluster": {
            "nodes": {
                "node1": {"ram": 64},
                "node2": {"cpu": 32, "ram": 128}
            },
            "region": "us-east-1"
        }
    }
    
    db.merge(merge_data)
    
    # Check deep merge
    assert db.get("cluster.name") == "prod-cluster"
    assert db.get("cluster.nodes.node1.cpu") == 16
    assert db.get("cluster.nodes.node1.ram") == 64
    assert db.get("cluster.nodes.node2.cpu") == 32
    assert db.get("cluster.region") == "us-east-1"

def test_merge_file(tmp_path):
    """Test merging from another YAML file."""
    # Create source file
    source_file = tmp_path / "source.yml"
    source_file.write_text("settings:\n  theme: dark\n  font: Roboto")
    
    # Create main DB
    main_file = str(tmp_path / "main.yml")
    db = YamlDB(filename=main_file)
    db.set("settings.theme", "light")
    db.set("app.name", "MyApp")
    
    db.merge(str(source_file))
    
    assert db.get("settings.theme") == "dark" # Overwritten
    assert db.get("settings.font") == "Roboto" # Added
    assert db.get("app.name") == "MyApp" # Preserved