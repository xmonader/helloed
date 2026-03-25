# helloed

A Python 3 / GTK3 text editor with syntax highlighting, file browser, regex toolkit, and integrated terminal.

## Features

- **Syntax Highlighting** - Powered by gtksourceview4
- **File Browser** - Built-in file browser with navigation
- **Regex Toolkit** - Test and debug regular expressions
- **Integrated Terminal** - VTE-based terminal (requires vte system package)
- **Code Navigation** - Python source code tree viewer
- **XML Viewer** - Visualize XML document structure
- **Find/Replace** - Advanced search and replace functionality
- **Go to Line** - Quick line navigation
- **Word Count** - Document statistics

## Requirements

- Python 3.8+
- GTK 3.0+
- GObject Introspection (gi)
- gtksourceview 4.x
- VTE 2.91 (optional, for terminal support)

## Installation

### System Dependencies (Ubuntu/Debian)

GTK3 and GObject introspection are required at the system level:

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
# Create virtual environment
make venv

# Activate it (optional - Makefile will auto-detect)
source .venv/bin/activate

# Install Python dependencies in venv
make install

# Run the application
make run
# Or with a specific file
make run FILE=/path/to/file.py
```

### Without Virtual Environment (System Python)

```bash
# Install Python dependencies globally
pip3 install --user -r requirements.txt

# Run directly
python3 src/hello.py
# Or open a specific file
python3 src/hello.py /path/to/file.py
```

### Makefile Targets

```bash
make help           # Show all available targets
make install        # Install Python dependencies
make install-dev    # Install dev dependencies (black, flake8, etc.)
make run            # Run the application
make run-debug      # Run with GTK inspector enabled
make check          # Check Python syntax
make clean          # Clean generated files
make setup          # Install system deps (Ubuntu/Debian)
make lint           # Run linters
make format         # Format code with black
```

## Project Structure

```
src/
├── hello.py              # Main entry point
├── widgets.py            # Custom GTK widgets
├── pyconsole.py          # Interactive Python console
├── terminal.py           # VTE terminal widget
├── gregextoolkitdialog.py  # Regex toolkit dialog
├── regextoolkitlib.py    # Regex utilities
├── regexlibapis.py       # Regex library API client
├── myhappymapper.py      # XML/HTML parser
└── ui/                   # Glade UI files
    ├── hello.glade
    └── gregextoolkitdialog.glade
```

## Migration Notes

This project was originally written for Python 2 and PyGTK (GTK 2). It has been modernized to use:

- **Python 3.8+** - Modern Python with type hints support
- **PyGObject (GTK 3)** - GObject introspection instead of PyGTK
- **gtksourceview 4** - Modern source editing component
- **urllib.request** - Python 3 HTTP client
- **html.parser** - Modern HTML parsing

## License

GPL-2.0-or-later - See LICENSE file for details.

## Author

Ahmed Youssef <xmonader@gmail.com>
