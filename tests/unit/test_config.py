"""Unit tests for configuration management."""

import unittest
import tempfile
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from helloed.config import ConfigManager, EditorConfig, AppConfig


class TestEditorConfig(unittest.TestCase):
    """Test EditorConfig dataclass."""
    
    def test_defaults(self):
        """Test default values."""
        config = EditorConfig()
        self.assertEqual(config.font_family, "Monospace")
        self.assertEqual(config.font_size, 10)
        self.assertTrue(config.use_spaces)


class TestAppConfig(unittest.TestCase):
    """Test AppConfig dataclass."""
    
    def test_defaults(self):
        """Test default values."""
        config = AppConfig()
        self.assertIsInstance(config.editor, EditorConfig)
        self.assertEqual(config.recent_files_limit, 10)


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        
        # Patch config locations
        self._orig_config_dir = None
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_singleton(self):
        """Test that ConfigManager is a singleton."""
        cm1 = ConfigManager()
        cm2 = ConfigManager()
        self.assertIs(cm1, cm2)
    
    def test_add_recent_file(self):
        """Test adding recent files."""
        cm = ConfigManager()
        cm.add_recent_file("/path/to/file1.txt")
        cm.add_recent_file("/path/to/file2.txt")
        
        recent = cm.get_recent_files()
        self.assertIn("/path/to/file1.txt", recent)
        self.assertIn("/path/to/file2.txt", recent)


if __name__ == '__main__':
    unittest.main()
