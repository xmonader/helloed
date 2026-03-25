"""Main Application class for helloed.

This module contains the Application class which serves as the
central coordinator for all application components.
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

from . import __version__
from .logging_config import get_logger
from .config import ConfigManager
from .events import events, EventMixin
from .plugins.base import plugins
from .core.document import Document
from .exceptions import HelloedError

logger = get_logger(__name__)


class Application(GObject.GObject, EventMixin):
    """Main application class.
    
    Manages the application lifecycle, windows, documents, and
    coordinates between different subsystems.
    
    Signals:
        document-opened: Emitted when a document is opened
        document-closed: Emitted when a document is closed
        window-created: Emitted when a new window is created
    """
    
    __gsignals__ = {
        'document-opened': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
        'document-closed': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
        'window-created': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }
    
    _instance: Optional['Application'] = None
    
    def __new__(cls, *args, **kwargs) -> 'Application':
        """Singleton pattern for Application."""
        if cls._instance is None:
            cls._instance = GObject.GObject.__new__(cls)
        return cls._instance
    
    def __init__(self, debug: bool = False, disable_plugins: bool = False):
        """Initialize application.
        
        Args:
            debug: Enable debug mode
            disable_plugins: Disable plugin loading
        """
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return
            
        GObject.GObject.__init__(self)
        EventMixin.__init__(self)
        
        self._debug = debug
        self._disable_plugins = disable_plugins
        self._initialized = True
        self._windows: List[Gtk.Window] = []
        self._documents: Dict[str, Document] = {}
        self._active_window: Optional[Gtk.Window] = None
        self._config = ConfigManager()
        
        # Initialize plugins
        if not disable_plugins:
            self._init_plugins()
        
        logger.info("helloed v%s initialized", __version__)
    
    def _init_plugins(self) -> None:
        """Initialize plugin system."""
        plugins.set_app(self)
        
        # Register built-in plugins
        from .plugins.base import AutoSavePlugin, WordCountPlugin
        plugins.register(AutoSavePlugin)
        plugins.register(WordCountPlugin)
        
        # Activate all plugins
        plugins.activate_all()
        
        logger.debug("Plugins initialized")
    
    def run(self) -> int:
        """Run the application.
        
        Returns:
            Exit code
        """
        logger.info("Starting main loop")
        
        # Create initial window if none exist
        if not self._windows:
            self.create_window()
        
        try:
            Gtk.main()
            return 0
        except Exception as e:
            logger.exception("Error in main loop: %s", e)
            return 1
    
    def quit(self) -> None:
        """Quit the application."""
        logger.info("Shutting down")
        
        # Save configuration
        self._config.save()
        
        # Deactivate plugins
        if not self._disable_plugins:
            plugins.deactivate_all()
        
        # Close all windows
        for window in self._windows[:]:
            self.close_window(window)
        
        # Cleanup event subscriptions
        self.cleanup_events()
        
        # Stop GTK main loop
        Gtk.main_quit()
    
    def create_window(self) -> Gtk.Window:
        """Create a new main window.
        
        Returns:
            New window instance
        """
        from .ui.main_window import MainWindow
        
        window = MainWindow(application=self)
        self._windows.append(window)
        
        window.connect("delete-event", self._on_window_close)
        window.show_all()
        
        self._active_window = window
        self.emit('window-created', window)
        
        logger.debug("Created new window")
        return window
    
    def close_window(self, window: Gtk.Window) -> None:
        """Close a window.
        
        Args:
            window: Window to close
        """
        if window in self._windows:
            self._windows.remove(window)
            window.destroy()
            
            # Update active window
            if self._active_window == window:
                self._active_window = self._windows[0] if self._windows else None
            
            logger.debug("Closed window")
        
        # Quit if no windows left
        if not self._windows:
            self.quit()
    
    def _on_window_close(self, window: Gtk.Window, event) -> bool:
        """Handle window close event.
        
        Returns:
            True to prevent closing, False to allow
        """
        # Check for unsaved changes
        # TODO: Check all documents in window
        self.close_window(window)
        return True  # We handle the close ourselves
    
    def open_file(self, filepath: Path, line: Optional[int] = None,
                  column: Optional[int] = None, 
                  new_window: bool = False) -> Optional[Document]:
        """Open a file.
        
        Args:
            filepath: Path to file
            line: Line number to jump to
            column: Column number to jump to
            new_window: Open in new window
            
        Returns:
            Document instance or None
        """
        filepath = Path(filepath).resolve()
        
        # Check if already open
        doc_id = str(filepath)
        if doc_id in self._documents:
            doc = self._documents[doc_id]
            # Switch to existing
            self._switch_to_document(doc, line, column)
            return doc
        
        # Create new document
        try:
            doc = Document(filepath=filepath)
            doc.load(filepath)
            self._documents[doc_id] = doc
            
            # Add to recent files
            self._config.add_recent_file(str(filepath))
            
            # Notify plugins
            plugins.broadcast_event('on_document_opened', doc)
            self.emit('document-opened', doc)
            
            # Show in window
            window = self._get_target_window(new_window)
            window.open_document(doc, line, column)
            
            logger.info("Opened file: %s", filepath)
            return doc
            
        except HelloedError as e:
            logger.error("Failed to open file: %s", e)
            self.show_error_dialog(f"Failed to open file:\n{e}")
            return None
    
    def close_document(self, doc: Document) -> bool:
        """Close a document.
        
        Args:
            doc: Document to close
            
        Returns:
            True if closed, False if cancelled
        """
        if doc.modified:
            # TODO: Show save confirmation dialog
            pass
        
        doc_id = str(doc.filepath) if doc.filepath else id(doc)
        if doc_id in self._documents:
            del self._documents[doc_id]
        
        plugins.broadcast_event('on_document_closed', doc)
        self.emit('document-closed', doc)
        
        logger.debug("Closed document: %s", doc.title)
        return True
    
    def _switch_to_document(self, doc: Document, line: Optional[int],
                           column: Optional[int]) -> None:
        """Switch to an already open document."""
        # Find window with this document
        for window in self._windows:
            if window.has_document(doc):
                window.present()
                window.focus_document(doc, line, column)
                return
        
        # Document exists but not in any window
        window = self._get_target_window(False)
        window.open_document(doc, line, column)
    
    def _get_target_window(self, new_window: bool) -> 'MainWindow':
        """Get target window for new content."""
        if new_window or not self._windows:
            return self.create_window()
        
        if self._active_window:
            return self._active_window
        
        return self._windows[0]
    
    def show_error_dialog(self, message: str, 
                         parent: Optional[Gtk.Window] = None) -> None:
        """Show an error dialog.
        
        Args:
            message: Error message
            parent: Parent window
        """
        dialog = Gtk.MessageDialog(
            transient_for=parent or self._active_window,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
    
    def get_recent_files(self) -> List[str]:
        """Get list of recent files."""
        return self._config.get_recent_files()
    
    @property
    def config(self) -> ConfigManager:
        """Get configuration manager."""
        return self._config
    
    @property
    def active_window(self) -> Optional[Gtk.Window]:
        """Get currently active window."""
        return self._active_window
    
    @property
    def documents(self) -> List[Document]:
        """Get all open documents."""
        return list(self._documents.values())
