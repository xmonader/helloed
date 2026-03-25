"""Unit tests for security module."""

import unittest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from helloed.security import SecurityManager, ALLOWED_TEXT_TYPES
from helloed.exceptions import SecurityError


class TestSecurityManager(unittest.TestCase):
    """Test SecurityManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.security = SecurityManager()
    
    def test_allowed_extensions(self):
        """Test that text extensions are allowed."""
        self.assertIn(".py", self.security.text_extensions)
        self.assertIn(".txt", self.security.text_extensions)
    
    def test_blocked_extensions(self):
        """Test that dangerous extensions are blocked."""
        self.assertIn(".exe", self.security.blocked_extensions)
    
    def test_validate_safe_path(self):
        """Test validating safe paths."""
        # Should not raise
        self.security.validate_file_path(Path("/home/user/file.txt"))
    
    def test_validate_traversal_path(self):
        """Test detecting path traversal."""
        with self.assertRaises(SecurityError):
            self.security.validate_file_path(Path("../etc/passwd"))
    
    def test_check_file_type_text(self):
        """Test checking text file type."""
        result = self.security.check_file_type(Path("test.py"))
        self.assertTrue(result)
    
    def test_check_file_type_blocked(self):
        """Test blocking dangerous file types."""
        with self.assertRaises(SecurityError):
            self.security.check_file_type(Path("malware.exe"))
    
    def test_safe_read_text_file(self):
        """Test safely reading a text file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Hello, World!")
            temp_path = Path(f.name)
        
        try:
            content = self.security.safe_read(temp_path)
            self.assertEqual(content, "Hello, World!")
        finally:
            temp_path.unlink()


if __name__ == '__main__':
    unittest.main()
