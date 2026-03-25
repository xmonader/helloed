"""Security utilities for helloed.

Provides file validation and security checks.
"""

import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, List, Set

from .logging_config import get_logger
from .exceptions import SecurityError, FileError

logger = get_logger(__name__)

# Maximum file sizes
MAX_TEXT_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed text MIME types
ALLOWED_TEXT_TYPES: Set[str] = {
    'text/plain',
    'text/x-python',
    'text/x-java',
    'text/x-c',
    'text/x-c++',
    'text/html',
    'text/css',
    'text/javascript',
    'application/javascript',
    'application/json',
    'application/xml',
    'text/xml',
    'text/markdown',
    'text/x-script.python',
    'text/x-shellscript',
    'text/x-perl',
    'text/x-ruby',
    'text/x-php',
    'text/x-go',
    'text/x-rust',
}

# Extensions that should be treated as text
TEXT_EXTENSIONS: Set[str] = {
    '.txt', '.py', '.pyw', '.js', '.jsx', '.ts', '.tsx',
    '.html', '.htm', '.css', '.scss', '.sass', '.less',
    '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.hxx',
    '.java', '.kt', '.scala', '.groovy',
    '.rb', '.erb', '.php', '.phps', '.phtml',
    '.go', '.rs', '.swift', '.m', '.mm',
    '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
    '.pl', '.pm', '.t',
    '.lua', '.vim', '.el', '.clj', '.cljs', '.cljc',
    '.hs', '.lhs', '.ml', '.mli', '.fs', '.fsx',
    '.r', '.R', '.matlab', '.m',
    '.sql', '.psql', '.mysql',
    '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg',
    '.md', '.rst', '.tex', '.latex',
    '.csv', '.tsv',
    '.log',
    '.gitignore', '.gitattributes', '.dockerignore',
    '.env', '.env.example', '.env.local',
    'Makefile', 'Dockerfile', 'Vagrantfile', 'Rakefile',
    '.htaccess', '.htpasswd',
    'README', 'LICENSE', 'CHANGELOG', 'CONTRIBUTING',
    '.editorconfig', '.eslintrc', '.prettierrc',
}

# Dangerous extensions to block
DANGEROUS_EXTENSIONS: Set[str] = {
    '.exe', '.dll', '.so', '.dylib', '.bin',
    '.bat', '.com', '.scr',
    '.shs', '.vbs', '.js', '.jse', '.wsf', '.wsh',
    '.ps1', '.ps1xml', '.ps2', '.ps2xml', '.psc1', '.psc2',
    '.msi', '.msp', '.mst',
    '.ade', '.adp', '.app', '.asp', '.bas', '.bat', '.cer',
    '.chm', '.cmd', '.cnt', '.com', '.cpl', '.crt', '.csh',
    '.der', '.fxp', '.gadget', '.grp', '.hlp', '.hpj', '.hta',
    '.inf', '.ins', '.isp', '.its', '.jar', '.jnlp', '.ksh',
    '.lib', '.lnk', '.mad', '.maf', '.mag', '.mam', '.maq',
    '.mar', '.mas', '.mat', '.mau', '.mav', '.maw', '.mcf',
    '.mda', '.mdb', '.mde', '.mdt', '.mdw', '.mdz', '.msc',
    '.msh', '.msh1', '.msh2', '.mshxml', '.msh1xml', '.msh2xml',
    '.msi', '.msp', '.mst', '.ops', '.osd', '.pcd', '.pif',
    '.pl', '.plg', '.prf', '.prg', '.pst', '.reg', '.scf',
    '.sct', '.shb', '.shs', '.ps1', '.ps2', '.psc1', '.psc2',
    '.tmp', '.url', '.vb', '.vbe', '.vbs', '.vsmacros', '.vss',
    '.vst', '.vsw', '.ws', '.wsc', '.wsf', '.wsh',
}


class SecurityManager:
    """Manages security checks for file operations."""
    
    def __init__(self):
        self.max_file_size = MAX_TEXT_FILE_SIZE
        self.allowed_types = ALLOWED_TEXT_TYPES.copy()
        self.text_extensions = TEXT_EXTENSIONS.copy()
        self.blocked_extensions = DANGEROUS_EXTENSIONS.copy()
    
    def validate_file_path(self, filepath: Path) -> None:
        """Validate a file path for security.
        
        Args:
            filepath: Path to validate
            
        Raises:
            SecurityError: If path is suspicious
        """
        path_str = str(filepath)
        
        # Check for path traversal
        normalized = filepath.resolve()
        if '..' in path_str:
            logger.warning("Potential path traversal attempt: %s", filepath)
            raise SecurityError(f"Path contains parent directory reference: {filepath}")
        
        # Check for null bytes
        if '\x00' in path_str:
            logger.warning("Null byte in path: %s", filepath)
            raise SecurityError(f"Invalid path (null byte): {filepath}")
    
    def check_file_type(self, filepath: Path) -> bool:
        """Check if file type is allowed.
        
        Args:
            filepath: Path to check
            
        Returns:
            True if file appears to be text
            
        Raises:
            SecurityError: If file type is blocked
        """
        # Check extension first
        ext = filepath.suffix.lower()
        name = filepath.name
        
        # Block dangerous extensions
        if ext in self.blocked_extensions:
            logger.warning("Blocked dangerous extension: %s", ext)
            raise SecurityError(f"File type not allowed: {ext}")
        
        # Allow known text extensions
        if ext in self.text_extensions or name in self.text_extensions:
            return True
        
        # Check MIME type
        mime_type, _ = mimetypes.guess_type(str(filepath))
        
        if mime_type:
            if mime_type in self.allowed_types:
                return True
            
            # Block executable MIME types
            if mime_type.startswith(('application/x-', 'application/octet')):
                logger.warning("Blocked binary MIME type: %s for %s", mime_type, filepath)
                raise SecurityError(f"Binary files not allowed: {filepath}")
        
        # If we can't determine type, check content
        return True
    
    def check_file_size(self, filepath: Path, max_size: Optional[int] = None) -> None:
        """Check file size.
        
        Args:
            filepath: Path to check
            max_size: Maximum allowed size (uses default if None)
            
        Raises:
            FileError: If file is too large
        """
        if not filepath.exists():
            return
        
        size = filepath.stat().st_size
        limit = max_size or self.max_file_size
        
        if size > limit:
            logger.warning("File too large: %s (%d bytes)", filepath, size)
            raise FileError(
                f"File too large: {size} bytes (max: {limit})",
                str(filepath)
            )
    
    def scan_content(self, content: str) -> None:
        """Scan content for suspicious patterns.
        
        Args:
            content: Content to scan
            
        Raises:
            SecurityError: If suspicious content detected
        """
        # Check for null bytes in content
        if '\x00' in content:
            raise SecurityError("Content contains null bytes")
        
        # Could add more checks here:
        # - Check for encoded exploits
        # - Check for suspicious Unicode
        # - etc.
    
    def safe_read(self, filepath: Path, encoding: str = "utf-8",
                  errors: str = "replace") -> str:
        """Safely read a file with all security checks.
        
        Args:
            filepath: Path to file
            encoding: File encoding
            errors: Error handling strategy
            
        Returns:
            File content
            
        Raises:
            SecurityError: If security check fails
            FileError: If file cannot be read
        """
        self.validate_file_path(filepath)
        self.check_file_type(filepath)
        self.check_file_size(filepath)
        
        try:
            with open(filepath, 'r', encoding=encoding, errors=errors) as f:
                content = f.read()
            
            self.scan_content(content)
            
            logger.debug("Safe read completed: %s", filepath)
            return content
            
        except UnicodeDecodeError as e:
            logger.warning("Encoding error in %s: %s", filepath, e)
            raise FileError(f"Cannot decode file as {encoding}: {e}", str(filepath))
        except Exception as e:
            logger.error("Failed to read file %s: %s", filepath, e)
            raise FileError(f"Failed to read file: {e}", str(filepath))
    
    def compute_hash(self, filepath: Path) -> str:
        """Compute MD5 hash of file.
        
        Args:
            filepath: Path to file
            
        Returns:
            MD5 hash string
        """
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def is_trusted_path(self, filepath: Path) -> bool:
        """Check if path is in a trusted location.
        
        Args:
            filepath: Path to check
            
        Returns:
            True if path is trusted
        """
        # Allow user's home directory
        home = Path.home()
        try:
            filepath.resolve().relative_to(home)
            return True
        except ValueError:
            pass
        
        # Allow /tmp for temporary files
        try:
            filepath.resolve().relative_to(Path("/tmp"))
            return True
        except ValueError:
            pass
        
        return False


# Global security manager instance
security = SecurityManager()
