"""Unit tests for Document model."""

import unittest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from helloed.core.document import Document, InsertTextCommand, DeleteTextCommand


class TestDocument(unittest.TestCase):
    """Test Document class."""
    
    def test_create_empty_document(self):
        """Test creating an empty document."""
        doc = Document()
        self.assertEqual(doc.content, "")
        self.assertFalse(doc.modified)
        self.assertIsNone(doc.filepath)
    
    def test_insert_text(self):
        """Test text insertion."""
        doc = Document()
        doc.insert("Hello", 0)
        
        self.assertEqual(doc.content, "Hello")
        self.assertTrue(doc.modified)
    
    def test_delete_text(self):
        """Test text deletion."""
        doc = Document()
        doc.insert("Hello World", 0)
        doc.delete(5, 11)  # Delete " World"
        
        self.assertEqual(doc.content, "Hello")
    
    def test_undo_insert(self):
        """Test undoing text insertion."""
        doc = Document()
        doc.insert("Hello", 0)
        
        self.assertTrue(doc.history.undo())
        self.assertEqual(doc.content, "")
    
    def test_redo_insert(self):
        """Test redoing text insertion."""
        doc = Document()
        doc.insert("Hello", 0)
        doc.history.undo()
        
        self.assertTrue(doc.history.redo())
        self.assertEqual(doc.content, "Hello")
    
    def test_load_file(self):
        """Test loading a file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_path = Path(f.name)
        
        try:
            doc = Document()
            doc.load(temp_path)
            
            self.assertEqual(doc.content, "Test content")
            self.assertEqual(doc.filepath, temp_path)
            self.assertFalse(doc.modified)
        finally:
            temp_path.unlink()
    
    def test_save_file(self):
        """Test saving a file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = Document()
            doc.insert("Test content", 0)
            
            save_path = Path(tmpdir) / "test.txt"
            saved_path = doc.save(save_path)
            
            self.assertEqual(saved_path, save_path)
            self.assertFalse(doc.modified)
            self.assertEqual(save_path.read_text(), "Test content")
    
    def test_word_count(self):
        """Test word counting."""
        doc = Document()
        doc.insert("Hello world test", 0)
        
        self.assertEqual(doc.word_count, 3)
    
    def test_line_count(self):
        """Test line counting."""
        doc = Document()
        doc.insert("Line 1\nLine 2\nLine 3", 0)
        
        self.assertEqual(doc.line_count, 3)
    
    def test_language_detection(self):
        """Test language detection from extension."""
        doc = Document(filepath=Path("test.py"))
        self.assertEqual(doc.metadata.language, "python")
        
        doc2 = Document(filepath=Path("test.js"))
        self.assertEqual(doc2.metadata.language, "javascript")


class TestCommands(unittest.TestCase):
    """Test command classes."""
    
    def test_insert_command(self):
        """Test InsertTextCommand."""
        doc = Document()
        cmd = InsertTextCommand(doc, "Hello", 0)
        
        cmd.execute()
        self.assertEqual(doc.content, "Hello")
        
        cmd.undo()
        self.assertEqual(doc.content, "")
    
    def test_delete_command(self):
        """Test DeleteTextCommand."""
        doc = Document()
        doc._set_content("Hello World")
        
        cmd = DeleteTextCommand(doc, 5, 11)
        cmd.execute()
        self.assertEqual(doc.content, "Hello")
        
        cmd.undo()
        self.assertEqual(doc.content, "Hello World")


if __name__ == '__main__':
    unittest.main()
