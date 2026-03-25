# Development Guide

## Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/xmonader/helloed.git
cd helloed

# Create virtual environment
make venv

# Install development dependencies
make install-dev
```

## Project Structure

```
helloed/
├── src/              # Source code
├── tests/            # Test suite
├── docs/             # Documentation
└── .github/          # GitHub Actions CI
```

## Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov
```

## Code Style

We use:
- **black** for code formatting
- **flake8** for linting

```bash
# Format code
make format

# Check formatting
make format-check

# Run linters
make lint
```

## Writing Tests

Tests are located in the `tests/` directory. Use pytest:

```python
# tests/test_feature.py
def test_something():
    assert True
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a Pull Request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.
