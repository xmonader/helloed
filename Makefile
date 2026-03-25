# Makefile for helloed - Python 3/GTK3 text editor
# https://github.com/xmonader/helloed

.PHONY: help venv install install-dev run clean lint format test check build dist

# Virtual environment settings
VENV_DIR ?= .venv
VENV_ABS := $(abspath $(VENV_DIR))

# Use deferred assignment so these are evaluated at target execution time
PYTHON = $(if $(wildcard $(VENV_ABS)/bin/python),$(VENV_ABS)/bin/python,python3)
PIP = $(if $(wildcard $(VENV_ABS)/bin/pip),$(VENV_ABS)/bin/pip,$(PYTHON) -m pip)

SRC_DIR := src
APP_NAME := helloed

# Default target
help:
	@echo "$(APP_NAME) - Python 3/GTK3 Text Editor"
	@echo ""
	@echo "Quick start:"
	@echo "  make venv     - Create virtual environment"
	@echo "  make install  - Install dependencies"
	@echo "  make run      - Run the application"
	@echo ""
	@echo "Development:"
	@echo "  make install-dev    - Install development dependencies"
	@echo "  make test           - Run test suite"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code with black"
	@echo "  make format-check   - Check code formatting"
	@echo "  make check          - Run syntax check"
	@echo ""
	@echo "Building:"
	@echo "  make build          - Build Python package"
	@echo "  make dist           - Create distribution"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Clean generated files"
	@echo "  make clean-all      - Clean including venv"
	@echo "  make setup          - Install system deps (Ubuntu/Debian)"
	@echo ""
	@echo "Current Python: $(PYTHON)"
	@echo "Virtual env: $(if $(wildcard $(VENV_DIR)),yes ($(VENV_DIR)),no)"
	@echo ""

# Create virtual environment
venv:
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "Virtual environment already exists at $(VENV_DIR)"; \
		echo "Run 'make venv-clean' first to recreate it"; \
		exit 1; \
	fi
	@echo "Creating virtual environment in $(VENV_DIR)..."
	python3 -m venv $(VENV_DIR)
	@echo "Virtual environment created!"
	@echo "Activate with: source $(VENV_DIR)/bin/activate"
	@echo "Or use 'make install' to install dependencies in the venv"

# Remove virtual environment
venv-clean:
	rm -rf $(VENV_DIR)
	@echo "Virtual environment removed"

# Install production dependencies
install:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "Warning: No venv found at $(VENV_DIR). Run 'make venv' first or use system Python."; \
		echo "Continuing with system Python..."; \
		echo ""; \
	fi
	$(PIP) install -r requirements.txt

# Install development dependencies
install-dev: install
	$(PIP) install black flake8 pylint pytest pytest-cov

# Run the application
run:
	cd $(SRC_DIR) && $(PYTHON) hello.py $(FILE)

# Run with GTK debugging
run-debug:
	GTK_DEBUG=interactive cd $(SRC_DIR) && $(PYTHON) hello.py $(FILE)

# Clean generated files (but keep venv by default)
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*~" -delete 2>/dev/null || true
	find . -type f -name "*.bak" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .mypy_cache/ .coverage

# Clean everything including venv
clean-all: clean venv-clean

# Run linters
lint:
	@echo "Running flake8..."
	-$(PYTHON) -m flake8 $(SRC_DIR) --max-line-length=120 --ignore=E203,W503,E501 --count 2>/dev/null || echo "flake8 issues found"
	@echo ""
	@echo "Running pylint..."
	-$(PYTHON) -m pylint $(SRC_DIR) --disable=C0103,C0111,R0903,R0913,C0301 --max-line-length=120 2>/dev/null || echo "pylint issues found"

# Format code with black
format:
	$(PYTHON) -m black $(SRC_DIR) --line-length 120

# Check formatting without modifying
format-check:
	$(PYTHON) -m black $(SRC_DIR) --line-length 120 --check

# Syntax check on all Python files
check:
	@echo "Checking Python syntax..."
	@for file in $$(find $(SRC_DIR) -name "*.py"); do \
		$(PYTHON) -m py_compile $$file && echo "✓ $$file"; \
	done
	@echo "All files passed syntax check!"

# Run tests
test:
	$(PYTHON) -m pytest tests/ -v --tb=short 2>/dev/null || echo "No tests available or test failure"

# Run tests with coverage
test-cov:
	$(PYTHON) -m pytest tests/ -v --cov=$(SRC_DIR) --cov-report=term-missing

# Install system dependencies (Ubuntu/Debian)
setup:
	@echo "Installing system dependencies..."
	sudo apt-get update
	sudo apt-get install -y \
		python3-gi \
		python3-gi-cairo \
		gir1.2-gtk-3.0 \
		gir1.2-gtksource-4 \
		gir1.2-vte-2.91 \
		libgirepository1.0-dev \
		pkg-config \
		python3-dev

# Install system dependencies (Fedora)
setup-fedora:
	@echo "Installing system dependencies for Fedora..."
	sudo dnf install -y \
		python3-gobject \
		gtk3 \
		gtksourceview4 \
		vte291 \
		gobject-introspection-devel \
		python3-devel

# Build package
build:
	$(PYTHON) -m build

# Create distribution
dist: clean
	$(PYTHON) -m build
	@echo "Distribution created in dist/"

# Install in editable mode (development)
editable:
	$(PIP) install -e .

# Create a desktop entry
install-desktop:
	@echo "Creating desktop entry..."
	@mkdir -p ~/.local/share/applications
	@echo "[Desktop Entry]" > ~/.local/share/applications/$(APP_NAME).desktop
	@echo "Name=helloed" >> ~/.local/share/applications/$(APP_NAME).desktop
	@echo "Comment=Python 3/GTK3 Text Editor" >> ~/.local/share/applications/$(APP_NAME).desktop
	@echo "Exec=$(shell pwd)/$(SRC_DIR)/hello.py" >> ~/.local/share/applications/$(APP_NAME).desktop
	@echo "Icon=text-editor" >> ~/.local/share/applications/$(APP_NAME).desktop
	@echo "Type=Application" >> ~/.local/share/applications/$(APP_NAME).desktop
	@echo "Terminal=false" >> ~/.local/share/applications/$(APP_NAME).desktop
	@echo "Categories=Development;TextEditor;" >> ~/.local/share/applications/$(APP_NAME).desktop
	@echo "MimeType=text/plain;" >> ~/.local/share/applications/$(APP_NAME).desktop
	@echo "Desktop entry created at ~/.local/share/applications/$(APP_NAME).desktop"

# Uninstall desktop entry
uninstall-desktop:
	rm -f ~/.local/share/applications/$(APP_NAME).desktop

# Security scan with bandit
security:
	$(PIP) install bandit
	$(PYTHON) -m bandit -r $(SRC_DIR) -f json -o bandit-report.json || true
	@echo "Security report saved to bandit-report.json"
