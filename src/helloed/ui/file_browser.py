"""File browser widget for helloed."""

import os
from pathlib import Path
from typing import Callable, Optional

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject

from ..logging_config import get_logger

logger = get_logger(__name__)


class FileBrowser(Gtk.Box):
    """File browser widget.
    
    Shows a tree view of the file system for navigation.
    """
    
    __gsignals__ = {
        'file-activated': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
        'directory-changed': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }
    
    def __init__(self):
        """Initialize file browser."""
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        
        self._current_path = Path.home()
        self._file_activated_callback: Optional[Callable[[Path], None]] = None
        
        self._build_ui()
        self._refresh()
    
    def _build_ui(self) -> None:
        """Build the UI."""
        # Path entry
        self._path_entry = Gtk.Entry()
        self._path_entry.connect("activate", self._on_path_entry_activated)
        self.pack_start(self._path_entry, False, False, 0)
        
        # Toolbar
        toolbar = Gtk.Toolbar()
        self.pack_start(toolbar, False, False, 0)
        
        # Up button
        up_icon = Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.SMALL_TOOLBAR)
        up_btn = Gtk.ToolButton(label="Up", icon_widget=up_icon)
        up_btn.set_tooltip_text("Go to parent directory")
        up_btn.connect("clicked", self._on_go_up)
        toolbar.insert(up_btn, -1)
        
        # Home button
        home_icon = Gtk.Image.new_from_icon_name("go-home", Gtk.IconSize.SMALL_TOOLBAR)
        home_btn = Gtk.ToolButton(label="Home", icon_widget=home_icon)
        home_btn.set_tooltip_text("Go to home directory")
        home_btn.connect("clicked", self._on_go_home)
        toolbar.insert(home_btn, -1)
        
        # Refresh button
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh", Gtk.IconSize.SMALL_TOOLBAR)
        refresh_btn = Gtk.ToolButton(label="Refresh", icon_widget=refresh_icon)
        refresh_btn.set_tooltip_text("Refresh file list")
        refresh_btn.connect("clicked", lambda _: self._refresh())
        toolbar.insert(refresh_btn, -1)
        
        # Tree view
        scrolled = Gtk.ScrolledWindow()
        self.pack_start(scrolled, True, True, 0)
        
        self._treeview = Gtk.TreeView()
        scrolled.add(self._treeview)
        
        # Columns
        # Icon column
        icon_renderer = Gtk.CellRendererPixbuf()
        # Use gicon instead of icon_name for better theme support
        icon_col = Gtk.TreeViewColumn("", icon_renderer, icon_name=0)
        icon_col.set_fixed_width(24)
        self._treeview.append_column(icon_col)
        
        # Name column
        text_renderer = Gtk.CellRendererText()
        name_col = Gtk.TreeViewColumn("Name", text_renderer, text=1)
        self._treeview.append_column(name_col)
        
        # Model
        self._store = Gtk.ListStore(str, str, str)  # icon, name, full_path
        self._treeview.set_model(self._store)
        
        # Connect signals
        self._treeview.connect("row-activated", self._on_row_activated)
    
    def _refresh(self) -> None:
        """Refresh the file list."""
        self._store.clear()
        self._path_entry.set_text(str(self._current_path))
        
        try:
            # Add parent directory
            if self._current_path != Path("/"):
                self._store.append(["go-up", "..", str(self._current_path.parent)])
            
            # List directory contents
            entries = sorted(self._current_path.iterdir(), 
                           key=lambda e: (not e.is_dir(), e.name.lower()))
            
            for entry in entries:
                if entry.is_dir():
                    icon = "folder"
                else:
                    # Try to get specific icon based on mime type
                    icon = self._get_file_icon(entry)
                
                self._store.append([icon, entry.name, str(entry)])
            
            self.emit('directory-changed', str(self._current_path))
            
        except PermissionError:
            logger.warning("Permission denied: %s", self._current_path)
        except Exception as e:
            logger.error("Failed to list directory: %s", e)
    
    def _get_file_icon(self, entry: Path) -> str:
        """Get appropriate icon name for file type.
        
        Args:
            entry: File path
            
        Returns:
            Icon name
        """
        if entry.is_dir():
            return "folder"
        
        # Map extensions to icons
        ext_map = {
            '.py': 'text-x-python',
            '.js': 'text-x-javascript',
            '.html': 'text-html',
            '.htm': 'text-html',
            '.css': 'text-css',
            '.c': 'text-x-c',
            '.cpp': 'text-x-c++',
            '.h': 'text-x-c',
            '.hpp': 'text-x-c++',
            '.java': 'text-x-java',
            '.rb': 'application-x-ruby',
            '.php': 'application-x-php',
            '.go': 'text-x-go',
            '.rs': 'text-x-rust',
            '.md': 'text-x-markdown',
            '.txt': 'text-plain',
            '.json': 'application-json',
            '.xml': 'application-xml',
            '.sh': 'application-x-shellscript',
            '.pdf': 'application-pdf',
            '.png': 'image-png',
            '.jpg': 'image-jpeg',
            '.jpeg': 'image-jpeg',
            '.gif': 'image-gif',
            '.svg': 'image-svg+xml',
        }
        
        ext = entry.suffix.lower()
        return ext_map.get(ext, 'text-x-generic')
    
    def set_path(self, path: Path) -> None:
        """Set current path.
        
        Args:
            path: Path to navigate to
        """
        self._current_path = Path(path).resolve()
        self._refresh()
    
    def _on_path_entry_activated(self, entry) -> None:
        """Handle path entry activation."""
        path = Path(entry.get_text())
        if path.exists() and path.is_dir():
            self.set_path(path)
    
    def _on_go_up(self, button) -> None:
        """Go to parent directory."""
        if self._current_path != Path("/"):
            self.set_path(self._current_path.parent)
    
    def _on_go_home(self, button) -> None:
        """Go to home directory."""
        self.set_path(Path.home())
    
    def _on_row_activated(self, treeview, path, column) -> None:
        """Handle row activation (double click or Enter)."""
        model = treeview.get_model()
        iter = model.get_iter(path)
        full_path = Path(model.get_value(iter, 2))
        
        if full_path.is_dir():
            self.set_path(full_path)
        else:
            self.emit('file-activated', full_path)
