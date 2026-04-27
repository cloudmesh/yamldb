# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Backend Strategy Pattern**: Decoupled storage logic into a strategy pattern (File, Binary, Encrypted) for better maintainability and extensibility.
- **Advanced API Methods**: Added `count()`, `merge()`, and `upsert()` for more powerful data manipulation.
- **Comment Preservation**: Migrated core engine to `ruamel.yaml` to preserve comments and formatting during read/write cycles.
- **Secure Storage**: Implemented `:encrypt:` backend using `cryptography.fernet` with PBKDF2 key derivation and unique salts. (Note: This backend is currently experimental; feedback is highly appreciated).
- **Binary Storage**: Implemented `:binary:` backend for high-performance, non-human-readable storage.
- **Advanced API**: Added `items_recursive()`, `find_all()`, `filter()`, and `update_many()` for complex data manipulation.
- **Wildcard Support**: Added support for `*` wildcards in `__getitem__` and `get()` for bulk retrieval.
- **Type Casting**: Added `get_as()` and explicit `cast` parameter in `set()` for type-safe operations.
- **Write Metrics**: Added `get_stats()` to monitor write efficiency and I/O reduction.
- **Export Tool**: Added `convert_to_yaml()` to export binary/encrypted data to human-readable YAML.

### Changed
- **Write Optimization**: Refined `auto_flush` and `_dirty` flag logic to significantly reduce disk I/O.
- **Concurrency**: Replaced manual lock files with `portalocker` for robust cross-platform advisory locking.
- **Project Structure**: Moved `run_webui.py` to the `bin/` directory.
- Extensively rewrote `README.md` to include detailed feature descriptions, rich code examples, and a comprehensive API reference.
- Updated `pyproject.toml` to use dynamic versioning from `VERSION` file.
- Updated `pyproject.toml` classifiers to include `Topic :: Database` and remove Python 3.7 support.

### Fixed
- **Persistence Bug**: Fixed `flush()` logic to ensure `:binary:` and `:encrypt:` backends persist data during `set()` calls.
- **Initialization Bug**: Fixed `__init__` to correctly create parent directories and initialize files across all backends.
- **Data Integrity**: Fixed a bug where root-level comments were lost during `load()` when merging data.
- **Type Consistency**: Fixed parent node type handling for binary and encrypted backends.
- Fixed build failure in GitHub Actions by removing unnecessary dependency on `cloudmesh-ai-common` in `tests/test_delete.py`.

## [1.0.10]

### Added
- Added atomic writes using temporary files to prevent data corruption during crashes.
- Added transaction support via a context manager to allow grouped updates with automatic rollback on failure.
- Added concurrency control using file-based locking to prevent data corruption from concurrent process access.
- Added comprehensive Python type hinting across the `YamlDB` class for better maintainability and IDE support.
- Added `tests/test_advanced.py` to verify atomic writes, transactions, and concurrency.
- Added `pytest-html` to `requirements-dev.txt` to enable HTML report generation during tests.

### Changed
- Migrated file system operations from `os.path` to `pathlib` for better cross-platform compatibility and cleaner code.

### Fixed
- Fixed `Makefile` by removing `pyenv` dependency and adding `pip` target to resolve CI failures.
- Fixed bug where `__len__` did not return the length of the database.

## [1.0.4]

### Added
- Added more versions for testing in `tox`.

### Changed
- Improved spelling in README.
- Added home page and other URLs to README.
- Removed `version.py` in favor of `VERSION` file.
- Switched to `src/` layout.
- Switched to `pyproject.toml` for project configuration.
- Improved test suite.

### Fixed
- Fixed bug in deletion of subelements.

---
*Note: Versions prior to 1.0.4 are no longer supported.*