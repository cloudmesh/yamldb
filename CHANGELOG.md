# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Extensively rewrote `README.md` to include detailed feature descriptions, rich code examples, and a comprehensive API reference.
- Added a Contributors section to `README.md`.
- Updated `pyproject.toml` to use dynamic versioning from `VERSION` file.
- Updated `pyproject.toml` classifiers to include `Topic :: Database` and remove Python 3.7 support.

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