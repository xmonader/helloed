"""
helloed - A Python 3/GTK3 text editor with syntax highlighting.

This package provides a modern, extensible text editor built with
PyGObject and GTK3.
"""

__version__ = "8.0.0"
__author__ = "Ahmed Youssef"
__email__ = "xmonader@gmail.com"
__license__ = "GPL-2.0-or-later"

from .logging_config import setup_logging
from .config import ConfigManager

# Initialize logging on import
setup_logging()

__all__ = ["__version__", "setup_logging", "ConfigManager"]
