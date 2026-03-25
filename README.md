# helloed

[![CI](https://github.com/xmonader/helloed/actions/workflows/ci.yml/badge.svg)](https://github.com/xmonader/helloed/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![GTK3](https://img.shields.io/badge/GTK-3.0+-green.svg)](https://gtk.org/)
[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

A Python 3/GTK3 text editor with syntax highlighting, file browser, and integrated tools.

![helloed screenshot](docs/screenshot.png)

## Features

- **Syntax Highlighting** - Powered by GtkSourceView 4
- **File Browser** - Built-in file browser with directory navigation
- **Regex Toolkit** - Test and debug regular expressions
- **Code Navigation** - Python source code tree viewer
- **XML Viewer** - Visualize XML document structure
- **Find/Replace** - Advanced search and replace functionality
- **Go to Line** - Quick line navigation
- **Word Count** - Document statistics
- **Paster Widget** - Upload code snippets to 0x0.st or save locally

## Requirements

- Python 3.8+
- GTK 3.0+
- GObject Introspection
- GtkSourceView 4
- (Optional) VTE 2.91 for integrated terminal

## Installation

### System Dependencies (Ubuntu/Debian)

```bash
sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
                     gir1.2-gtksource-4 gir1.2-vte-2.91 \
                     libgirepository1.0-dev
```

Or use the Makefile:
```bash
make setup  # Ubuntu/Debian
# or
make setup-fedora  # Fedora
```

### Using Virtual Environment (Recommended)

```bash
# Full setup
make venv install run

# Step by step
make venv
make install
make run
```

### Without Virtual Environment

```bash
pip3 install --user -r requirements.txt
python3 src/hello.py
```

## Usage

```bash
# Run the editor
make run

# Open a specific file
make run FILE=/path/to/file.py
```

## Development

```bash
# Setup development environment
make install-dev

# Run tests
make test

# Check code formatting
make format-check

# Format code
make format

# Run linters
make lint
```

## Project Structure

```
helloed/
├── src/                    # Source code
│   ├── hello.py           # Main entry point
│   ├── widgets.py         # Custom GTK widgets
│   ├── pyconsole.py       # Interactive Python console
│   ├── terminal.py        # VTE terminal widget
│   ├── gregextoolkitdialog.py  # Regex toolkit
│   ├── regextoolkitlib.py # Regex utilities
│   ├── myhappymapper.py   # XML/HTML parser
│   └── ui/                # Glade UI files
├── tests/                 # Test suite
├── docs/                  # Documentation
├── .github/workflows/     # CI/CD configuration
├── Makefile              # Build automation
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Project metadata
├── README.md             # This file
├── CONTRIBUTING.md       # Contribution guidelines
├── CODE_OF_CONDUCT.md    # Community standards
├── CHANGELOG.md          # Version history
└── LICENSE               # GPL v2 license
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.

## License

This project is licensed under the GPL-2.0-or-later License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original author: Ahmed Youssef (xmonader@gmail.com)
- Thanks to all contributors

---

**Note:** This project was originally written for Python 2/PyGTK and has been modernized to Python 3/GTK3.
