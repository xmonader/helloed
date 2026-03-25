"""Document model for helloed.

Provides the core document data model with undo/redo support
via the Command pattern.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Callable, Any
from datetime import datetime
import hashlib

from ..logging_config import get_logger
from ..exceptions import FileError, ValidationError

logger = get_logger(__name__)


class Command(ABC):
    """Abstract base class for undoable commands."""
    
    def __init__(self, description: str = ""):
        self.description = description
        self.timestamp = datetime.now()
        self.executed = False
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass
    
    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass
    
    @abstractmethod
    def redo(self) -> None:
        """Redo the command (default is execute)."""
        self.execute()


class InsertTextCommand(Command):
    """Command to insert text."""
    
    def __init__(self, document: 'Document', text: str, position: int):
        super().__init__(f"Insert '{text[:20]}...' at {position}")
        self.document = document
        self.text = text
        self.position = position
    
    def execute(self) -> None:
        content = self.document.content
        new_content = content[:self.position] + self.text + content[self.position:]
        self.document._set_content(new_content)
        self.executed = True
        logger.debug("Executed: %s", self.description)
    
    def undo(self) -> None:
        content = self.document.content
        end_pos = self.position + len(self.text)
        new_content = content[:self.position] + content[end_pos:]
        self.document._set_content(new_content)
        logger.debug("Undone: %s", self.description)


class DeleteTextCommand(Command):
    """Command to delete text."""
    
    def __init__(self, document: 'Document', start: int, end: int):
        super().__init__(f"Delete from {start} to {end}")
        self.document = document
        self.start = start
        self.end = end
        self._deleted_text = ""
    
    def execute(self) -> None:
        content = self.document.content
        self._deleted_text = content[self.start:self.end]
        new_content = content[:self.start] + content[self.end:]
        self.document._set_content(new_content)
        self.executed = True
        logger.debug("Executed: %s", self.description)
    
    def undo(self) -> None:
        content = self.document.content
        new_content = content[:self.start] + self._deleted_text + content[self.start:]
        self.document._set_content(new_content)
        logger.debug("Undone: %s", self.description)


class ReplaceTextCommand(Command):
    """Command to replace text."""
    
    def __init__(self, document: 'Document', old_text: str, new_text: str, 
                 start: int = 0):
        super().__init__(f"Replace '{old_text[:20]}...' with '{new_text[:20]}...'")
        self.document = document
        self.old_text = old_text
        self.new_text = new_text
        self.start = start
        self._position = -1
    
    def execute(self) -> None:
        content = self.document.content
        self._position = content.find(self.old_text, self.start)
        if self._position != -1:
            new_content = (content[:self._position] + self.new_text + 
                          content[self._position + len(self.old_text):])
            self.document._set_content(new_content)
        self.executed = True
        logger.debug("Executed: %s", self.description)
    
    def undo(self) -> None:
        if self._position != -1:
            content = self.document.content
            new_content = (content[:self._position] + self.old_text +
                          content[self._position + len(self.new_text):])
            self.document._set_content(new_content)
        logger.debug("Undone: %s", self.description)


class CommandHistory:
    """Manages undo/redo history.
    
    Implements the Command pattern for undoable operations.
    """
    
    def __init__(self, max_history: int = 1000):
        self._history: List[Command] = []
        self._position: int = -1
        self._max_history = max_history
        self._undo_callback: Optional[Callable[[Command], None]] = None
        self._redo_callback: Optional[Callable[[Command], None]] = None
    
    def set_callbacks(self, undo_cb: Callable[[Command], None] = None,
                      redo_cb: Callable[[Command], None] = None) -> None:
        """Set callbacks for undo/redo operations."""
        self._undo_callback = undo_cb
        self._redo_callback = redo_cb
    
    def execute(self, command: Command) -> None:
        """Execute a command and add to history.
        
        Args:
            command: Command to execute
        """
        # Execute the command
        command.execute()
        
        # Truncate any redo history
        self._history = self._history[:self._position + 1]
        
        # Add new command
        self._history.append(command)
        self._position += 1
        
        # Enforce max history
        if len(self._history) > self._max_history:
            self._history.pop(0)
            self._position -= 1
        
        logger.debug("Command added to history: %s", command.description)
    
    def undo(self) -> bool:
        """Undo the last command.
        
        Returns:
            True if undo was performed
        """
        if self._position >= 0:
            command = self._history[self._position]
            command.undo()
            self._position -= 1
            
            if self._undo_callback:
                self._undo_callback(command)
            
            logger.debug("Undo: %s", command.description)
            return True
        
        logger.debug("Nothing to undo")
        return False
    
    def redo(self) -> bool:
        """Redo the next command.
        
        Returns:
            True if redo was performed
        """
        if self._position < len(self._history) - 1:
            self._position += 1
            command = self._history[self._position]
            command.redo()
            
            if self._redo_callback:
                self._redo_callback(command)
            
            logger.debug("Redo: %s", command.description)
            return True
        
        logger.debug("Nothing to redo")
        return False
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self._position >= 0
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self._position < len(self._history) - 1
    
    def clear(self) -> None:
        """Clear all history."""
        self._history.clear()
        self._position = -1
        logger.debug("Command history cleared")
    
    def get_undo_description(self) -> Optional[str]:
        """Get description of next undo action."""
        if self.can_undo():
            return self._history[self._position].description
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Get description of next redo action."""
        if self.can_redo():
            return self._history[self._position + 1].description
        return None


@dataclass
class DocumentMetadata:
    """Metadata about a document."""
    encoding: str = "utf-8"
    language: str = ""
    line_ending: str = "\n"
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)


class Document:
    """Represents a text document.
    
    The Document class manages the content, metadata, and history
    of a text document. It provides methods for editing with
    full undo/redo support.
    """
    
    def __init__(self, filepath: Optional[Path] = None):
        self._filepath: Optional[Path] = filepath
        self._content: str = ""
        self._modified: bool = False
        self._metadata = DocumentMetadata()
        self._history = CommandHistory()
        self._hash: str = ""
        
        if filepath:
            self._metadata.language = self._detect_language(filepath)
    
    # Properties
    @property
    def filepath(self) -> Optional[Path]:
        """Get document file path."""
        return self._filepath
    
    @filepath.setter
    def filepath(self, value: Path) -> None:
        self._filepath = value
        self._metadata.language = self._detect_language(value)
    
    @property
    def content(self) -> str:
        """Get document content."""
        return self._content
    
    @property
    def modified(self) -> bool:
        """Check if document has unsaved changes."""
        return self._modified
    
    @property
    def metadata(self) -> DocumentMetadata:
        """Get document metadata."""
        return self._metadata
    
    @property
    def history(self) -> CommandHistory:
        """Get command history for undo/redo."""
        return self._history
    
    @property
    def title(self) -> str:
        """Get document title for display."""
        if self._filepath:
            return self._filepath.name
        return "Untitled"
    
    @property
    def word_count(self) -> int:
        """Get word count."""
        return len(self._content.split())
    
    @property
    def line_count(self) -> int:
        """Get line count."""
        return len(self._content.splitlines())
    
    @property
    def char_count(self) -> int:
        """Get character count."""
        return len(self._content)
    
    # Internal methods
    def _set_content(self, content: str) -> None:
        """Set content directly (used by commands)."""
        self._content = content
        self._modified = True
        self._metadata.modified_at = datetime.now()
        self._update_hash()
    
    def _update_hash(self) -> None:
        """Update content hash for change detection."""
        self._hash = hashlib.md5(self._content.encode()).hexdigest()
    
    def _detect_language(self, filepath: Path) -> str:
        """Detect language from file extension."""
        ext = filepath.suffix.lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.xml': 'xml',
            '.json': 'json',
            '.md': 'markdown',
            '.c': 'c',
            '.cpp': 'cpp',
            '.h': 'c',
            '.java': 'java',
            '.sh': 'sh',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.sql': 'sql',
            '.yaml': 'yaml',
            '.yml': 'yaml',
        }
        return language_map.get(ext, "")
    
    # Public methods
    def insert(self, text: str, position: int) -> None:
        """Insert text at position with undo support.
        
        Args:
            text: Text to insert
            position: Position to insert at
        """
        cmd = InsertTextCommand(self, text, position)
        self._history.execute(cmd)
    
    def delete(self, start: int, end: int) -> None:
        """Delete text range with undo support.
        
        Args:
            start: Start position
            end: End position
        """
        cmd = DeleteTextCommand(self, start, end)
        self._history.execute(cmd)
    
    def replace(self, old_text: str, new_text: str, start: int = 0) -> int:
        """Replace text with undo support.
        
        Args:
            old_text: Text to replace
            new_text: Replacement text
            start: Start position for search
            
        Returns:
            Position where replacement occurred, or -1 if not found
        """
        pos = self._content.find(old_text, start)
        if pos != -1:
            cmd = ReplaceTextCommand(self, old_text, new_text, pos)
            self._history.execute(cmd)
        return pos
    
    def load(self, filepath: Path, encoding: str = "utf-8") -> None:
        """Load document from file.
        
        Args:
            filepath: Path to file
            encoding: File encoding
            
        Raises:
            FileError: If file cannot be loaded
        """
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                self._content = f.read()
            
            self._filepath = filepath
            self._modified = False
            self._metadata.encoding = encoding
            self._metadata.accessed_at = datetime.now()
            self._metadata.language = self._detect_language(filepath)
            self._update_hash()
            self._history.clear()
            
            logger.info("Loaded document: %s", filepath)
            
        except FileNotFoundError:
            raise FileError(f"File not found: {filepath}", str(filepath))
        except UnicodeDecodeError as e:
            raise FileError(f"Cannot decode file: {e}", str(filepath))
        except Exception as e:
            raise FileError(f"Failed to load file: {e}", str(filepath))
    
    def save(self, filepath: Optional[Path] = None, 
             encoding: Optional[str] = None) -> Path:
        """Save document to file.
        
        Args:
            filepath: Path to save to (uses existing if None)
            encoding: Encoding to use (uses existing if None)
            
        Returns:
            Path where file was saved
            
        Raises:
            FileError: If file cannot be saved
            ValidationError: If no filepath is specified
        """
        save_path = filepath or self._filepath
        if not save_path:
            raise ValidationError("No filepath specified for save")
        
        save_encoding = encoding or self._metadata.encoding
        
        try:
            # Create backup if file exists
            if save_path.exists() and save_path != self._filepath:
                backup_path = save_path.with_suffix(save_path.suffix + "~")
                backup_path.write_text(save_path.read_text(), encoding=save_encoding)
            
            # Write file
            with open(save_path, 'w', encoding=save_encoding) as f:
                f.write(self._content)
            
            self._filepath = save_path
            self._modified = False
            self._metadata.encoding = save_encoding
            self._metadata.modified_at = datetime.now()
            
            logger.info("Saved document: %s", save_path)
            return save_path
            
        except PermissionError:
            raise FileError(f"Permission denied: {save_path}", str(save_path))
        except Exception as e:
            raise FileError(f"Failed to save file: {e}", str(save_path))
    
    def get_line(self, line_number: int) -> str:
        """Get a specific line by number (0-indexed).
        
        Args:
            line_number: Line number (0-indexed)
            
        Returns:
            Line content or empty string if out of range
        """
        lines = self._content.splitlines()
        if 0 <= line_number < len(lines):
            return lines[line_number]
        return ""
    
    def get_line_start(self, line_number: int) -> int:
        """Get the character position at the start of a line.
        
        Args:
            line_number: Line number (0-indexed)
            
        Returns:
            Character position
        """
        lines = self._content.splitlines(True)
        pos = 0
        for i, line in enumerate(lines):
            if i == line_number:
                return pos
            pos += len(line)
        return pos
    
    def clear(self) -> None:
        """Clear document content and history."""
        self._content = ""
        self._filepath = None
        self._modified = False
        self._history.clear()
        self._metadata = DocumentMetadata()
        logger.debug("Document cleared")
