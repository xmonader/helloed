"""Logging configuration for helloed."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path for log output
        format_string: Optional custom format string
        
    Returns:
        The root logger instance
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]
    
    # Add file handler if specified or use default
    if log_file is None:
        log_dir = Path.home() / ".config" / "helloed" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "helloed.log"
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, mode='a'))
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers,
        force=True  # Python 3.8+
    )
    
    # Create logger for this package
    logger = logging.getLogger("helloed")
    logger.debug("Logging initialized at level %s", logging.getLevelName(level))
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"helloed.{name}")
