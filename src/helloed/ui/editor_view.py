"""Editor view widget for helloed."""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')
from gi.repository import Gtk, GtkSource, Pango

from ..core.document import Document
from ..logging_config import get_logger

logger = get_logger(__name__)


class EditorView(Gtk.Box):
    """Source code editor view.
    
    Wraps a GtkSourceView for editing documents.
    """
    
    def __init__(self, document: Document):
        """Initialize editor view.
        
        Args:
            document: Document to edit
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        
        self._document = document
        self._buffer = None
        self._view = None
        
        self._build_ui()
        self._load_document()
    
    def _build_ui(self) -> None:
        """Build the UI."""
        # Scrolled window for editor
        scrolled = Gtk.ScrolledWindow()
        self.pack_start(scrolled, True, True, 0)
        
        # Create source buffer and view
        self._buffer = GtkSource.Buffer()
        self._view = GtkSource.View.new_with_buffer(self._buffer)
        
        # Configure view
        self._view.set_show_line_numbers(True)
        self._view.set_highlight_current_line(True)
        self._view.set_auto_indent(True)
        self._view.set_indent_width(4)
        self._view.set_insert_spaces_instead_of_tabs(True)
        self._view.set_wrap_mode(Gtk.WrapMode.NONE)
        
        # Font
        font = Pango.FontDescription("Monospace 10")
        self._view.override_font(font)
        
        scrolled.add(self._view)
        
        # Connect signals
        self._buffer.connect("changed", self._on_buffer_changed)
    
    def _load_document(self) -> None:
        """Load document content into editor."""
        # Set content
        self._buffer.set_text(self._document.content)
        
        # Set language
        lang_id = self._document.metadata.language
        if lang_id:
            lang_manager = GtkSource.LanguageManager.get_default()
            lang = lang_manager.get_language(lang_id)
            if lang:
                self._buffer.set_language(lang)
    
    def _on_buffer_changed(self, buffer) -> None:
        """Handle buffer changes."""
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        text = buffer.get_text(start, end, True)
        
        # Update document content
        self._document._set_content(text)
    
    def goto_line(self, line: int, column: int = 1) -> None:
        """Move cursor to line and column.
        
        Args:
            line: Line number (1-indexed)
            column: Column number (1-indexed)
        """
        # Convert to 0-indexed
        line = max(0, line - 1)
        column = max(0, column - 1)
        
        iter = self._buffer.get_iter_at_line_offset(line, column)
        self._buffer.place_cursor(iter)
        self._view.scroll_to_mark(self._buffer.get_insert(), 0.25, True, 0.5, 0.5)
    
    @property
    def document(self) -> Document:
        """Get the document being edited."""
        return self._document
