"""Basic tests for helloed."""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestImports(unittest.TestCase):
    """Test that modules can be imported."""
    
    def test_gi_imports(self):
        """Test GObject introspection imports."""
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk, Gdk, GObject, Pango
        except ImportError as e:
            self.skipTest(f"GTK not available: {e}")
    
    def test_lxml_import(self):
        """Test lxml import."""
        try:
            from lxml import etree
        except ImportError:
            self.skipTest("lxml not available")


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_word_counter(self):
        """Test word counter functionality."""
        # Import after ensuring path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        try:
            from widgets import WC
            wc = WC("Hello world\nThis is a test")
            self.assertEqual(wc.nlines(), 2)
            self.assertEqual(wc.nwords(), 6)
            self.assertEqual(wc.nchars(), 26)
        except ImportError:
            self.skipTest("widgets module not available")


class TestProjectStructure(unittest.TestCase):
    """Test project structure."""
    
    def test_required_files_exist(self):
        """Test that required project files exist."""
        root = os.path.join(os.path.dirname(__file__), '..')
        required_files = [
            'README.md',
            'LICENSE',
            'requirements.txt',
            'Makefile',
            'pyproject.toml',
            'CONTRIBUTING.md',
            'CODE_OF_CONDUCT.md',
            'CHANGELOG.md',
        ]
        for filename in required_files:
            filepath = os.path.join(root, filename)
            self.assertTrue(os.path.exists(filepath), f"Missing {filename}")


if __name__ == '__main__':
    unittest.main()
