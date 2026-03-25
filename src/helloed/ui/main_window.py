"""Main window for helloed.

This is the primary application window containing the editor,
side panes, and toolbars.
"""

from pathlib import Path
from typing import Optional, List

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

from ..logging_config import get_logger
from ..core.document import Document
from ..events import EventMixin

logger = get_logger(__name__)


class MainWindow(Gtk.Window, EventMixin):
    """Main application window.
    
    Contains the source editor, file browser, bottom panel,
    and all toolbars and menus.
    """
    
    __gsignals__ = {
        'document-changed': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
    }
    
    def __init__(self, application=None):
        """Initialize main window.
        
        Args:
            application: Application instance
        """
        Gtk.Window.__init__(self, title="helloed")
        EventMixin.__init__(self)
        
        self._app = application
        self._current_document: Optional[Document] = None
        self._documents: List[Document] = []
        
        self._setup_window()
        self._build_ui()
        self._connect_signals()
    
    def _setup_window(self) -> None:
        """Setup window properties."""
        from ..config import ConfigManager
        config = ConfigManager().config.window
        
        self.set_default_size(config.width, config.height)
        
        if config.maximized:
            self.maximize()
    
    def _build_ui(self) -> None:
        """Build the user interface."""
        # Main vertical box
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)
        
        # Menu bar
        self._build_menubar(vbox)
        
        # Toolbar
        self._build_toolbar(vbox)
        
        # Main content area
        self._hpaned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        vbox.pack_start(self._hpaned, True, True, 0)
        
        # Left sidebar
        self._build_sidebar()
        
        # Center editor area
        self._build_editor_area()
        
        # Bottom panel
        self._build_bottom_panel()
        
        # Status bar
        self._statusbar = Gtk.Statusbar()
        vbox.pack_start(self._statusbar, False, False, 0)
    
    def _build_menubar(self, parent: Gtk.Box) -> None:
        """Build menu bar."""
        menubar = Gtk.MenuBar()
        parent.pack_start(menubar, False, False, 0)
        
        # File menu
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="_File", use_underline=True)
        file_item.set_submenu(file_menu)
        menubar.append(file_item)
        
        # New
        new_item = Gtk.MenuItem(label="_New", use_underline=True)
        new_item.connect("activate", self._on_new)
        file_menu.append(new_item)
        
        # Open
        open_item = Gtk.MenuItem(label="_Open", use_underline=True)
        open_item.connect("activate", self._on_open)
        file_menu.append(open_item)
        
        file_menu.append(Gtk.SeparatorMenuItem())
        
        # Save
        save_item = Gtk.MenuItem(label="_Save", use_underline=True)
        save_item.connect("activate", self._on_save)
        file_menu.append(save_item)
        
        # Save As
        saveas_item = Gtk.MenuItem(label="Save _As", use_underline=True)
        saveas_item.connect("activate", self._on_save_as)
        file_menu.append(saveas_item)
        
        file_menu.append(Gtk.SeparatorMenuItem())
        
        # Quit
        quit_item = Gtk.MenuItem(label="_Quit", use_underline=True)
        quit_item.connect("activate", self._on_quit)
        file_menu.append(quit_item)
    
    def _build_toolbar(self, parent: Gtk.Box) -> None:
        """Build toolbar."""
        toolbar = Gtk.Toolbar()
        parent.pack_start(toolbar, False, False, 0)
        
        # New button
        new_btn = Gtk.ToolButton(stock_id="gtk-new")
        new_btn.connect("clicked", self._on_new)
        toolbar.insert(new_btn, -1)
        
        # Open button
        open_btn = Gtk.ToolButton(stock_id="gtk-open")
        open_btn.connect("clicked", self._on_open)
        toolbar.insert(open_btn, -1)
        
        # Save button
        save_btn = Gtk.ToolButton(stock_id="gtk-save")
        save_btn.connect("clicked", self._on_save)
        toolbar.insert(save_btn, -1)
    
    def _build_sidebar(self) -> None:
        """Build left sidebar."""
        # Import and create file browser
        from .file_browser import FileBrowser
        self._file_browser = FileBrowser()
        self._file_browser.connect("file-activated", self._on_file_browser_activated)
        
        # Create notebook for sidebar tabs
        sidebar_notebook = Gtk.Notebook()
        sidebar_notebook.append_page(
            self._file_browser,
            Gtk.Label(label="Files")
        )
        
        self._hpaned.pack1(sidebar_notebook, False, False)
        self._hpaned.set_position(200)
    
    def _build_editor_area(self) -> None:
        """Build center editor area."""
        self._vpaned = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        self._hpaned.pack2(self._vpaned, True, False)
        
        # Editor notebook (for multiple files)
        self._editor_notebook = Gtk.Notebook()
        self._editor_notebook.set_scrollable(True)
        self._vpaned.pack1(self._editor_notebook, True, False)
    
    def _build_bottom_panel(self) -> None:
        """Build bottom panel."""
        bottom_notebook = Gtk.Notebook()
        self._vpaned.pack2(bottom_notebook, False, False)
        self._vpaned.set_position(500)
        
        # Add terminal or console
        label = Gtk.Label(label="Terminal not available")
        bottom_notebook.append_page(label, Gtk.Label(label="Terminal"))
    
    def _connect_signals(self) -> None:
        """Connect signal handlers."""
        self.connect("destroy", self._on_destroy)
        self.connect("key-press-event", self._on_key_press)
    
    def open_document(self, doc: Document, line: Optional[int] = None,
                     column: Optional[int] = None) -> None:
        """Open a document in the editor.
        
        Args:
            doc: Document to open
            line: Line number to jump to
            column: Column number to jump to
        """
        if doc not in self._documents:
            self._documents.append(doc)
            
            # Create editor view for document
            from .editor_view import EditorView
            editor = EditorView(document=doc)
            
            # Add to notebook
            label = Gtk.Label(label=doc.title)
            page_num = self._editor_notebook.append_page(editor, label)
            self._editor_notebook.set_tab_reorderable(editor, True)
            
            editor.show_all()
        else:
            # Find existing editor
            for i in range(self._editor_notebook.get_n_pages()):
                editor = self._editor_notebook.get_nth_page(i)
                if hasattr(editor, 'document') and editor.document == doc:
                    page_num = i
                    break
            else:
                logger.error("Document in list but no editor found")
                return
        
        # Switch to document
        self._editor_notebook.set_current_page(page_num)
        self._current_document = doc
        self._update_title()
        
        # Jump to position if specified
        if line is not None:
            editor.goto_line(line, column or 1)
        
        self.emit('document-changed', doc)
    
    def has_document(self, doc: Document) -> bool:
        """Check if window has a document open.
        
        Args:
            doc: Document to check
            
        Returns:
            True if document is open in this window
        """
        return doc in self._documents
    
    def focus_document(self, doc: Document, line: Optional[int] = None,
                      column: Optional[int] = None) -> None:
        """Focus an already open document.
        
        Args:
            doc: Document to focus
            line: Line to jump to
            column: Column to jump to
        """
        self.open_document(doc, line, column)
    
    def _update_title(self) -> None:
        """Update window title."""
        if self._current_document:
            title = self._current_document.title
            if self._current_document.modified:
                title = f"*{title}"
            self.set_title(f"{title} - helloed")
        else:
            self.set_title("helloed")
    
    # Signal handlers
    def _on_new(self, widget) -> None:
        """Handle new document request."""
        doc = Document()
        self.open_document(doc)
    
    def _on_open(self, widget) -> None:
        """Handle open file request."""
        dialog = Gtk.FileChooserDialog(
            title="Open File",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL,
            "Open", Gtk.ResponseType.OK
        )
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = Path(dialog.get_filename())
            if self._app:
                self._app.open_file(filepath)
        
        dialog.destroy()
    
    def _on_save(self, widget) -> None:
        """Handle save request."""
        if self._current_document:
            try:
                self._current_document.save()
                self._update_title()
            except Exception as e:
                logger.error("Save failed: %s", e)
                self._show_error(f"Failed to save: {e}")
    
    def _on_save_as(self, widget) -> None:
        """Handle save as request."""
        # TODO: Implement save as
        pass
    
    def _on_quit(self, widget) -> None:
        """Handle quit request."""
        if self._app:
            self._app.quit()
        else:
            self.destroy()
    
    def _on_destroy(self, widget) -> None:
        """Handle window destroy."""
        logger.debug("MainWindow destroyed")
    
    def _on_key_press(self, widget, event) -> bool:
        """Handle key press events."""
        # Handle keyboard shortcuts
        from gi.repository import Gdk
        
        # Ctrl+O: Open
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.keyval == Gdk.KEY_o:
                self._on_open(widget)
                return True
            # Ctrl+N: New
            elif event.keyval == Gdk.KEY_n:
                self._on_new(widget)
                return True
            # Ctrl+S: Save
            elif event.keyval == Gdk.KEY_s:
                self._on_save(widget)
                return True
        
        return False
    
    def _on_file_browser_activated(self, browser, filepath: Path) -> None:
        """Handle file browser activation."""
        if self._app:
            self._app.open_file(filepath)
    
    def _show_error(self, message: str) -> None:
        """Show error dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
    
    @property
    def current_document(self) -> Optional[Document]:
        """Get current document."""
        return self._current_document
