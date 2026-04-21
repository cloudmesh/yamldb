# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Fixed bug where `__len__` did not return the length of the database.

### Changed
- Migrated file system operations from `os.path` to `pathlib` for better cross-platform compatibility and cleaner code.

### Added
- Added atomic writes to prevent data corruption.
- Added transaction support for grouped updates.
- Added concurrency control using file locking.
- Added comprehensive type hinting for better maintainability and IDE support.
- Added `pytest-html` to `requirements-dev.txt` to enable HTML report generation during tests.

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