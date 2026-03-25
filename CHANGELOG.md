# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern Python 3.8+ support
- PyGObject (GTK3) migration
- New PasterWidget with 0x0.st upload support
- Local file saving in PasterWidget
- Makefile with venv support
- pyproject.toml for modern packaging
- requirements.txt for dependencies
- CONTRIBUTING.md, CODE_OF_CONDUCT.md
- This CHANGELOG.md

### Changed
- Migrated from PyGTK to PyGObject
- Updated gtksourceview2 to GtkSource 4
- Converted Glade files to GTK3 format
- Modernized all GTK constants
- Improved code structure and organization

### Removed
- Python 2 support
- HPaste service integration (service is defunct)
- Deprecated gtk.glade usage

## [6.0.0] - 2008 (Legacy)

### Original Release
- Initial PyGTK text editor
- Syntax highlighting via gtksourceview2
- File browser
- Regex toolkit
- Integrated terminal (VTE)
- Code navigation for Python
- XML viewer

---

## Release Notes Template

```
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Now removed features

### Fixed
- Bug fixes

### Security
- Security improvements
```
