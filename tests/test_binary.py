import pytest
import os
from yamldb.YamlDB import YamlDB

@pytest.fixture
def temp_bin_file(tmp_path):
    """Provides a temporary file path for the binary database."""
    return str(tmp_path / "test_binary_db.bin")

def test_binary_storage_basic(temp_bin_file):
    """Test that binary backend correctly saves and loads data."""
    data = {
        "cluster": {
            "name": "hpc-cluster-01",
            "nodes": {
                "node01": {"gpu_count": 8, "status": "online"},
                "node02": {"gpu_count": 4, "status": "maintenance"}
            }
        },
        "global": {"version": "2.4.1"}
    }
    
    # Create and save
    db = YamlDB(data=data, filename=temp_bin_file, backend=":binary:")
    
    # Load in a new instance
    db2 = YamlDB(filename=temp_bin_file, backend=":binary:")
    
    assert db2["cluster.name"] == "hpc-cluster-01"
    assert db2["cluster.nodes.node01.gpu_count"] == 8
    assert db2["cluster.nodes.node02.status"] == "maintenance"
    assert db2["global.version"] == "2.4.1"

def test_binary_set_get(temp_bin_file):
    """Test setting and getting values in binary mode."""
    db = YamlDB(filename=temp_bin_file, backend=":binary:")
    db.set("cluster.nodes.node03.gpu_count", "16", cast=int)
    db.set("cluster.nodes.node03.status", "online")
    
    assert db["cluster.nodes.node03.gpu_count"] == 16
    assert db["cluster.nodes.node03.status"] == "online"

def test_convert_to_yaml(temp_bin_file, tmp_path):
    """Test exporting binary data to a human-readable YAML file."""
    data = {"cluster": {"name": "hpc-cluster-01", "nodes": {"node01": {"gpu": 8}}}}
    db = YamlDB(data=data, filename=temp_bin_file, backend=":binary:")
    
    yaml_export = str(tmp_path / "export.yml")
    db.convert_to_yaml(yaml_export)
    
    # Verify the exported file is valid YAML and contains the data
    with open(yaml_export, "r") as f:
        content = f.read()
        assert "name: hpc-cluster-01" in content
        assert "gpu: 8" in content

def test_binary_transaction_rollback(temp_bin_file):
    """Test that transactions still work correctly with binary backend."""
    db = YamlDB(filename=temp_bin_file, backend=":binary:")
    db.set("cluster.status", "operational")
    
    try:
        with db.transaction():
            db.set("cluster.status", "down")
            raise RuntimeError("Crash")
    except RuntimeError:
        pass
        
    assert db["cluster.status"] == "operational"
