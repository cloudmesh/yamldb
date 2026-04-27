import pytest
from yamldb.YamlDB import YamlDB

@pytest.fixture
def infra_db(tmp_path):
    """Provides a YamlDB instance populated with infrastructure data."""
    db_file = str(tmp_path / "infra_test.yml")
    data = {
        "cluster": {
            "name": "hpc-cluster-01",
            "nodes": {
                "node01": {"gpu_count": 8, "status": "online", "os": "ubuntu-22.04"},
                "node02": {"gpu_count": 4, "status": "maintenance", "os": "ubuntu-22.04"},
                "node03": {"gpu_count": 16, "status": "online", "os": "rhel-9"},
            },
            "network": {
                "switch01": {"ip": "10.0.0.1", "status": "online"},
                "switch02": {"ip": "10.0.0.2", "status": "offline"},
            }
        }
    }
    db = YamlDB(data=data, filename=db_file)
    return db

def test_standard_get(infra_db):
    """Verify that standard dot-notation still works."""
    assert infra_db["cluster.name"] == "hpc-cluster-01"
    assert infra_db.get("cluster.nodes.node01.gpu_count") == 8

def test_simple_wildcard(infra_db):
    """Test basic wildcard retrieval (a.*.b)."""
    # Get all node statuses
    statuses = infra_db.get("cluster.nodes.*.status")
    assert isinstance(statuses, list)
    assert len(statuses) == 3
    assert "online" in statuses
    assert "maintenance" in statuses

def test_deep_wildcard(infra_db):
    """Test deeply nested wildcard retrieval."""
    # Get all GPU counts across all nodes
    gpu_counts = infra_db["cluster.nodes.*.gpu_count"]
    assert sorted(gpu_counts) == [4, 8, 16]

def test_multiple_wildcards(infra_db):
    """Test multiple wildcards in a single path."""
    # This should return a list of lists or a flattened list depending on JMESPath
    # cluster.*.*.status -> statuses of nodes and switches
    all_statuses = infra_db.get("cluster.*.*.status")
    assert isinstance(all_statuses, list)
    # node01, node02, node03, switch01, switch02
    assert len(all_statuses) == 5

def test_non_existent_wildcard(infra_db):
    """Verify that non-matching wildcards return an empty list or None."""
    # Path that doesn't exist
    results = infra_db.get("cluster.nodes.*.non_existent_key")
    # JMESPath usually returns null or empty list for non-matching projections
    assert results is None or results == []

def test_wildcard_with_get_as(infra_db):
    """Verify that get_as handles wildcard lists (should return the list as is)."""
    # Since get_as is designed for single values, it should return the list
    # if the underlying get() returns a list.
    gpu_counts = infra_db.get_as("cluster.nodes.*.gpu_count", list)
    assert gpu_counts == [8, 4, 16] or sorted(gpu_counts) == [4, 8, 16]