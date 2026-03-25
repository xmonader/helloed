# Installation Guide

## System Requirements

- Linux (Ubuntu/Debian/Fedora)
- Python 3.8 or higher
- GTK 3.0 or higher

## Installing Dependencies

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    gir1.2-gtksource-4 \
    gir1.2-vte-2.91 \
    libgirepository1.0-dev \
    pkg-config
```

Or simply run:
```bash
make setup
```

### Fedora

```bash
sudo dnf install -y \
    python3-gobject \
    gtk3 \
    gtksourceview4 \
    vte291 \
    gobject-introspection-devel
```

Or run:
```bash
make setup-fedora
```

## Installing helloed

### From Source

```bash
# Clone the repository
git clone https://github.com/xmonader/helloed.git
cd helloed

# Create virtual environment and install
make venv install

# Run the application
make run
```

### Development Install

```bash
make install-dev
```

## Troubleshooting

### GTK not found

If you see errors about GTK not being found, ensure you have the system dependencies installed (see above).

### Import errors

Make sure you're using the virtual environment or have installed the Python dependencies:
```bash
pip install -r requirements.txt
```
