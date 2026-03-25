"""Custom exceptions for helloed."""


class HelloedError(Exception):
    """Base exception for all helloed errors."""
    pass


class FileError(HelloedError):
    """Raised when file operations fail."""
    
    def __init__(self, message: str, path: str = ""):
        super().__init__(message)
        self.path = path


class ConfigError(HelloedError):
    """Raised when configuration operations fail."""
    pass


class PluginError(HelloedError):
    """Raised when plugin operations fail."""
    
    def __init__(self, message: str, plugin_name: str = ""):
        super().__init__(message)
        self.plugin_name = plugin_name


class SecurityError(HelloedError):
    """Raised when a security check fails."""
    pass


class ValidationError(HelloedError):
    """Raised when data validation fails."""
    pass


class CommandError(HelloedError):
    """Raised when a command operation fails."""
    pass
