# YamlDB

[![GitHub Repo](https://img.shields.io/badge/github-repo-green.svg)](https://github.com/cloudmesh/yamldb)
[![PyPI Versions](https://img.shields.io/pypi/pyversions/yamldb.svg)](https://pypi.org/project/yamldb)
[![PyPI Version](https://img.shields.io/pypi/v/yamldb.svg)](https://pypi.org/project/yamldb/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![GitHub issues](https://img.shields.io/github/issues/cloudmesh/yamldb.svg)](https://github.com/cloudmesh/yamldb/issues)
[![Contributors](https://img.shields.io/github/contributors/cloudmesh/yamldb.svg)](https://github.com/cloudmesh/yamldb/graphs/contributors)

[![Linux](https://img.shields.io/badge/OS-Linux-orange.svg)](https://www.linux.org/)
[![macOS](https://img.shields.io/badge/OS-macOS-lightgrey.svg)](https://www.apple.com/macos)
[![Windows](https://img.shields.io/badge/OS-Windows-blue.svg)](https://www.microsoft.com/windows)

YamlDB is a lightweight, easy-to-use file-based database that uses YAML as its storage format. It allows you to treat a YAML file as a dictionary in your Python application, providing a balance between the simplicity of a flat file and the functionality of a database.

## Key Features

- **Human Readable**: Data is stored in standard YAML, making it easy to inspect and edit manually.
- **Dot Notation**: Access and set nested values using dot-separated keys (e.g., `db["user.profile.name"]`).
- **Powerful Querying**: Integrated with [JMESPath](https://jmespath.org/) for complex searching and filtering.
- **Data Integrity**:
    - **Atomic Writes**: Uses temporary files to ensure that crashes during saving don't corrupt your database.
    - **Transactions**: Supports atomic transactions via a context manager; changes are rolled back if an error occurs.
    - **Concurrency Control**: Implements file-based locking to prevent data corruption when multiple processes access the same file.
- **Flexible Backends**: Supports both persistent file storage (`:file:`) and volatile in-memory storage (`:memory:`).

## Installation

```bash
pip install yamldb
```

*Note: Requires Python 3.8 or newer.*

## Quick Start

### Basic CRUD Operations

```python
from yamldb import YamlDB

# Initialize the database
db = YamlDB(filename="data.yml")

# Set values (creates parents automatically)
db["user.name"] = "Gregor"
db["user.age"] = 30
db["settings.theme"] = "dark"

# Get values with an optional default
name = db.get("user.name") # "Gregor"
city = db.get("user.city", default="Unknown") # "Unknown"

# Delete a key
db.delete("settings.theme")

# Save changes to disk
db.save()
```

### Advanced Searching with JMESPath

YamlDB uses JMESPath for querying, allowing you to filter and transform your data.

```python
# Sample data: {"users": [{"name": "Gregor", "age": 30}, {"name": "Alice", "age": 25}]}
db["users"] = [{"name": "Gregor", "age": 30}, {"name": "Alice", "age": 25}]

# Find users older than 28
results = db.search("[?age > `28`]")
# [{'name': 'Gregor', 'age': 30}]

# Get only the names of all users
names = db.search("users[].name")
# ['Gregor', 'Alice']
```

### Transactions

Use the `transaction()` context manager to ensure a group of updates are applied atomically.

```python
try:
    with db.transaction():
        db["account.balance"] = 100
        db["account.status"] = "active"
        # If an exception occurs here, both changes are rolled back
        raise RuntimeError("Something went wrong!")
except RuntimeError:
    print("Transaction rolled back!")

# Balance remains unchanged if it was previously different
```

### Concurrency and Locking

YamlDB automatically handles file locking to prevent concurrent processes from corrupting the data. If a lock is held by another process, YamlDB will wait for a timeout period before raising a `RuntimeError`.

## API Reference

### `YamlDB(filename="yamldb.yml", backend=":file:", data=None)`
- `filename`: Path to the YAML file.
- `backend`: Either `":file:"` (default) or `":memory:"`.
- `data`: Optional initial dictionary to populate the DB.

### Core Methods
- `get(key, default=None)`: Retrieves a value using dot notation.
- `set(key, value)`: Sets a value using dot notation. Also supports `db[key] = value`.
- `delete(key)`: Removes a key using dot notation.
- `save(filename=None)`: Atomically writes the current state to disk.
- `load(filename=None)`: Reloads the data from the file.
- `search(query)`: Executes a JMESPath query against the data.
- `transaction()`: Context manager for atomic updates.
- `keys()`: Returns a list of all keys in the database.
- `clear()`: Removes all data from the database.
- `dict()`: Returns the internal data as a standard Python dictionary.
- `yaml()`: Returns the data as a YAML string.

## Development and Tests

The best way to contribute is with issues and pull requests.

```bash
git clone https://github.com/cloudmesh/yamldb.git
cd yamldb
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
```

Run tests with:
```bash
pytest -v tests/
```

## Alternatives

- [jmespath](https://jmespath.org/): The query language used by YamlDB.
- [TinyDB](https://tinydb.readthedocs.io/): Another lightweight document database.
- [nosqlite](https://github.com/shaunduncan/nosqlite): A NoSQL wrapper for SQLite.
- [MongoDB](https://www.mongodb.com/): A full-featured document database (YamlDB is a simpler alternative for small-scale needs).

## Contributors

Special thanks to all the contributors who have helped improve YamlDB. You can see the full list of contributors on [GitHub](https://github.com/cloudmesh/yamldb/graphs/contributors).

## Acknowledgments

Continued work was in part funded by the NSF CyberTraining: CIC: CyberTraining for Students and Technologies from Generation Z with the award numbers 1829704 and 2200409.
