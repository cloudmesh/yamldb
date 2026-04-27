# YamlDB

YamlDB is a file-based database that uses YAML for storage. It provides an API for managing nested configuration data with support for atomic writes, concurrency locking, and advanced querying.

## Features

- **Nested Key Access**: Use dot-notation (e.g., `user.profile.name`) to get or set values.
- **Atomic Writes**: Writes to a temporary file before replacing the original to prevent data loss.
- **Concurrency Locking**: Uses system-level advisory locks (`portalocker`) to prevent corruption during concurrent access.
- **Comment Preservation**: Uses `ruamel.yaml` to preserve comments and formatting in your YAML files.
- **Write Optimization**: An `auto_flush` mechanism and `_dirty` flag reduce disk I/O.
- **Advanced Querying**: Integrated JMESPath support for complex searches.
- **Type Casting**: Hybrid system for explicit casting during storage and retrieval.
- **Transactions**: Atomic bulk updates with full rollback support.
- **CLI Tool**: Manage your YAML databases directly from the terminal.

## Installation

### Standard Installation
```bash
pip install yamldb
```

### Installation with Encryption Support
To use the `:encrypt:` backend, you need the `cryptography` library:
```bash
pip install "yamldb[encrypt]"
```

## Quick Start

### Programmatic API (Computing Infrastructure Example)

Use cases include managing infrastructure manifests, cluster configurations, and node metadata.

```python
from yamldb import YamlDB

# Initialize DB for cluster configuration
db = YamlDB(filename="cluster_config.yml", auto_flush=True)

# Define infrastructure components using dot-notation
db.set("cluster.name", "hpc-cluster-01")
db.set("cluster.nodes.node01.gpu_count", "8", cast=int)
db.set("cluster.nodes.node01.status", "online")
db.set("cluster.nodes.node02.gpu_count", "4", cast=int)
db.set("cluster.nodes.node02.status", "maintenance")

# Retrieve infrastructure details
gpu_count = db.get_as("cluster.nodes.node01.gpu_count", int)
status = db.get("cluster.nodes.node01.status")

# Advanced Search (JMESPath)
# Find all nodes that are currently 'online'
online_nodes = db.search("cluster.nodes.[?status=='online']")

# Bulk Updates in a Transaction (e.g., updating cluster version)
with db.transaction():
    db.set("cluster.version", "2.4.1")
    db.set("cluster.last_updated", "2026-04-27")
    # If an exception occurs, the version won't be partially updated
```

### CLI Usage

The `yamldb` CLI allows direct interaction with YAML databases from the terminal.

#### General Usage
```bash
yamldb [OPTIONS] COMMAND [ARGS]...
```

#### Commands

**`get`**: Retrieve a value using dot-notation.
```bash
yamldb get <file> <key>
# Example: yamldb get config.yml user.profile.name
```

**`set`**: Set a value. Automatically creates parent keys if they don't exist.
```bash
yamldb set <file> <key> <value>
# Example: yamldb set config.yml app.version 1.2.0
```

**`delete`**: Remove a key from the database.
```bash
yamldb delete <file> <key>
# Example: yamldb delete config.yml user.old_setting
```

**`search`**: Query the database using JMESPath expressions.
```bash
yamldb search <file> <query>
# Example: yamldb search config.yml "[?status=='active']"
```

**`stats`**: Display write efficiency and I/O statistics.
```bash
yamldb stats <file>
# Example: yamldb stats config.yml
```

## Advanced API Reference

### `items_recursive()`
A generator that yields all leaf nodes in the database as `(dot_notation_key, value)` pairs. This allows auditing of infrastructure states.
```python
for key, value in db.items_recursive():
    print(f"{key}: {value}")
# Output: cluster.nodes.node01.gpu_count: 8 ...
```

### `find_all(value)` & `filter(predicate)`
Locate infrastructure components based on their state.
```python
# Find all nodes that are in 'maintenance' mode
maintenance_nodes = db.find_all("maintenance")

# Find all nodes with more than 4 GPUs
high_capacity_nodes = db.filter(lambda v: isinstance(v, int) and v > 4)
```

### `update_many(data_dict)`
Perform multiple infrastructure updates atomically.
```python
db.update_many({
    "cluster.nodes.node01.status": "offline",
    "cluster.nodes.node01.last_reboot": "2026-04-27",
    "cluster.global.maintenance_mode": True
})
```

### Wildcard Retrieval
You can use the `*` wildcard in `get()` or via bracket access to retrieve multiple values across the database. This is powered by JMESPath under the hood.

```python
# Get the status of ALL nodes in the cluster
# Returns a list: ['online', 'maintenance', 'online']
statuses = db.get("cluster.nodes.*.status")

# Get the GPU count for all nodes
# Returns a list: [8, 4, 16]
gpu_counts = db["cluster.nodes.*.gpu_count"]
```

### Write Efficiency (`get_stats`)
Track how many disk writes were avoided thanks to the `_dirty` flag.
```python
stats = db.get_stats()
print(f"Write Efficiency: {stats['write_efficiency']}")
```

## Configuration

- `filename`: Path to the YAML file.
- `backend`: 
    - `:file:` (default): Standard human-readable YAML storage.
    - `:memory:`: In-memory storage (no disk I/O).
    - `:binary:`: High-performance binary storage using JSON serialization.
- `auto_flush`: If `True` (default), changes are written to disk immediately unless inside a transaction.

## Advanced Features

### Binary Storage
For applications requiring smaller file sizes and faster I/O, use the `:binary:` backend.
```python
db = YamlDB(filename="data.bin", backend=":binary:")
db.set("metrics.cpu", 45)

# Export binary data to human-readable YAML for debugging
db.convert_to_yaml("debug_export.yml")
```

### Secure Storage (Encryption)
For sensitive data, use the `:encrypt:` backend. This encrypts the **entire database file** (including keys and structure) using AES-128 symmetric encryption.

> **Note**: The `:encrypt:` backend is currently **experimental**. We are actively refining its implementation and would greatly appreciate your feedback!

```python
# Initialize an encrypted database
db = YamlDB(
    filename="secrets.enc", 
    backend=":encrypt:", 
    password="your-strong-password"
)

# Use it exactly like a normal YamlDB
db.set("cluster.admin_password", "super-secret-123")
db.set("cluster.api_key", "abc-123-def-456")

# The file 'secrets.enc' is now a binary blob that is unreadable 
# without the correct password.
```

### Web UI Prototype
YamlDB comes with a lightweight Web UI for visual data management. This is a prototype designed to demonstrate how easily YamlDB can be integrated into other frameworks (such as FastAPI).

**To run the Web UI:**
1. Install dependencies: `pip install fastapi uvicorn`
2. Run the server: `python yamldb/bin/run_webui.py`
3. Open your browser to `http://localhost:8000`

The Web UI allows you to browse the database tree, set/delete values via dot-notation, and monitor write efficiency in real-time.
