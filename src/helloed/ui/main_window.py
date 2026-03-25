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
        
        # Edit menu
        edit_menu = Gtk.Menu()
        edit_item = Gtk.MenuItem(label="_Edit", use_underline=True)
        edit_item.set_submenu(edit_menu)
        menubar.append(edit_item)
        
        # Cut
        cut_item = Gtk.MenuItem(label="Cu_t", use_underline=True)
        cut_item.connect("activate", self._on_cut)
        edit_menu.append(cut_item)
        
        # Copy
        copy_item = Gtk.MenuItem(label="_Copy", use_underline=True)
        copy_item.connect("activate", self._on_copy)
        edit_menu.append(copy_item)
        
        # Paste
        paste_item = Gtk.MenuItem(label="_Paste", use_underline=True)
        paste_item.connect("activate", self._on_paste)
        edit_menu.append(paste_item)
        
        edit_menu.append(Gtk.SeparatorMenuItem())
        
        # Find/Replace
        find_item = Gtk.MenuItem(label="_Find/Replace", use_underline=True)
        find_item.connect("activate", self._on_find)
        edit_menu.append(find_item)
        
        # Go to Line
        goto_item = Gtk.MenuItem(label="_Go to Line", use_underline=True)
        goto_item.connect("activate", self._on_goto_line)
        edit_menu.append(goto_item)
        
        # View menu
        view_menu = Gtk.Menu()
        view_item = Gtk.MenuItem(label="_View", use_underline=True)
        view_item.set_submenu(view_menu)
        menubar.append(view_item)
        
        # Line numbers toggle
        line_nums_item = Gtk.CheckMenuItem(label="Show _Line Numbers")
        line_nums_item.set_active(True)
        line_nums_item.connect("toggled", self._on_toggle_line_numbers)
        view_menu.append(line_nums_item)
        
        # Tools menu
        tools_menu = Gtk.Menu()
        tools_item = Gtk.MenuItem(label="_Tools", use_underline=True)
        tools_item.set_submenu(tools_menu)
        menubar.append(tools_item)
        
        # Regex Toolkit
        regex_item = Gtk.MenuItem(label="_Regex Toolkit", use_underline=True)
        regex_item.connect("activate", self._on_regex_toolkit)
        tools_menu.append(regex_item)
        
        # Word Count
        wc_item = Gtk.MenuItem(label="_Word Count", use_underline=True)
        wc_item.connect("activate", self._on_word_count)
        tools_menu.append(wc_item)
        
        # Help menu
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="_Help", use_underline=True)
        help_item.set_submenu(help_menu)
        menubar.append(help_item)
        
        # About
        about_item = Gtk.MenuItem(label="_About", use_underline=True)
        about_item.connect("activate", self._on_about)
        help_menu.append(about_item)
    
    def _build_toolbar(self, parent: Gtk.Box) -> None:
        """Build toolbar."""
        toolbar = Gtk.Toolbar()
        parent.pack_start(toolbar, False, False, 0)
        
        # New button
        new_icon = Gtk.Image.new_from_icon_name("document-new", Gtk.IconSize.LARGE_TOOLBAR)
        new_btn = Gtk.ToolButton(label="New", icon_widget=new_icon)
        new_btn.set_tooltip_text("Create new document")
        new_btn.connect("clicked", self._on_new)
        toolbar.insert(new_btn, -1)
        
        # Open button
        open_icon = Gtk.Image.new_from_icon_name("document-open", Gtk.IconSize.LARGE_TOOLBAR)
        open_btn = Gtk.ToolButton(label="Open", icon_widget=open_icon)
        open_btn.set_tooltip_text("Open file")
        open_btn.connect("clicked", self._on_open)
        toolbar.insert(open_btn, -1)
        
        # Save button
        save_icon = Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.LARGE_TOOLBAR)
        save_btn = Gtk.ToolButton(label="Save", icon_widget=save_icon)
        save_btn.set_tooltip_text("Save document")
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
        """Build bottom panel with terminal, console, scribble, paster."""
        self._bottom_notebook = Gtk.Notebook()
        self._vpaned.pack2(self._bottom_notebook, False, False)
        self._vpaned.set_position(500)
        
        # Terminal
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from terminal import GeditTerminal
            self._terminal = GeditTerminal()
            self._bottom_notebook.append_page(
                self._terminal, 
                Gtk.Label(label="Terminal")
            )
        except Exception as e:
            logger.warning("Terminal not available: %s", e)
            label = Gtk.Label(label="Terminal not available\n(install vte/gir1.2-vte)")
            self._bottom_notebook.append_page(label, Gtk.Label(label="Terminal"))
        
        # Python Console
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from pyconsole import Console
            self._console = Console()
            self._bottom_notebook.append_page(
                self._console,
                Gtk.Label(label="Python Console")
            )
        except Exception as e:
            logger.warning("Python console not available: %s", e)
            label = Gtk.Label(label="Console not available")
            self._bottom_notebook.append_page(label, Gtk.Label(label="Console"))
        
        # Scribble pad
        scrolled = Gtk.ScrolledWindow()
        self._scribble = Gtk.TextView()
        scrolled.add(self._scribble)
        self._bottom_notebook.append_page(
            scrolled,
            Gtk.Label(label="Scribble")
        )
        
        # Paster widget
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent))
            from widgets import PasterWidget
            scrolled = Gtk.ScrolledWindow()
            self._paster = PasterWidget()
            scrolled.add(self._paster)
            self._bottom_notebook.append_page(
                scrolled,
                Gtk.Label(label="Paster")
            )
        except Exception as e:
            logger.warning("Paster widget not available: %s", e)
    
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
        logger.debug("New document requested")
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
    
    def _on_cut(self, widget) -> None:
        """Handle cut request."""
        page = self._editor_notebook.get_current_page()
        editor = self._editor_notebook.get_nth_page(page)
        if editor and hasattr(editor, '_view'):
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            editor._view.get_buffer().cut_clipboard(clipboard, True)
    
    def _on_copy(self, widget) -> None:
        """Handle copy request."""
        page = self._editor_notebook.get_current_page()
        editor = self._editor_notebook.get_nth_page(page)
        if editor and hasattr(editor, '_view'):
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            editor._view.get_buffer().copy_clipboard(clipboard)
    
    def _on_paste(self, widget) -> None:
        """Handle paste request."""
        page = self._editor_notebook.get_current_page()
        editor = self._editor_notebook.get_nth_page(page)
        if editor and hasattr(editor, '_view'):
            clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
            editor._view.get_buffer().paste_clipboard(clipboard, None, True)
    
    def _on_find(self, widget) -> None:
        """Handle find/replace request."""
        self._show_find_replace_dialog()
    
    def _show_find_replace_dialog(self) -> None:
        """Show find/replace dialog."""
        dialog = Gtk.Dialog(
            title="Find and Replace",
            transient_for=self,
            modal=False
        )
        dialog.set_default_size(400, 200)
        
        # Get content area
        content = dialog.get_content_area()
        content.set_spacing(6)
        content.set_margin_top(12)
        content.set_margin_bottom(12)
        content.set_margin_start(12)
        content.set_margin_end(12)
        
        # Search entry
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        content.add(search_box)
        search_label = Gtk.Label(label="Find:")
        search_box.add(search_label)
        self._find_entry = Gtk.Entry()
        self._find_entry.set_hexpand(True)
        search_box.add(self._find_entry)
        
        # Replace entry
        replace_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        content.add(replace_box)
        replace_label = Gtk.Label(label="Replace:")
        replace_box.add(replace_label)
        self._replace_entry = Gtk.Entry()
        self._replace_entry.set_hexpand(True)
        replace_box.add(self._replace_entry)
        
        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        button_box.set_homogeneous(True)
        content.add(button_box)
        
        find_btn = Gtk.Button(label="Find Next")
        find_btn.connect("clicked", self._on_find_next)
        button_box.add(find_btn)
        
        replace_btn = Gtk.Button(label="Replace")
        replace_btn.connect("clicked", self._on_replace)
        button_box.add(replace_btn)
        
        replace_all_btn = Gtk.Button(label="Replace All")
        replace_all_btn.connect("clicked", self._on_replace_all)
        button_box.add(replace_all_btn)
        
        close_btn = Gtk.Button(label="Close")
        close_btn.connect("clicked", lambda w: dialog.destroy())
        button_box.add(close_btn)
        
        content.show_all()
        dialog.show()
        self._find_dialog = dialog
    
    def _on_find_next(self, widget) -> None:
        """Find next occurrence."""
        if not self._current_document:
            return
        
        search_text = self._find_entry.get_text()
        if not search_text:
            return
        
        # Get current editor
        page = self._editor_notebook.get_current_page()
        editor = self._editor_notebook.get_nth_page(page)
        if not editor or not hasattr(editor, '_view'):
            return
        
        buffer = editor._buffer
        cursor = buffer.get_insert()
        start_iter = buffer.get_iter_at_mark(cursor)
        
        # Search forward
        found = start_iter.forward_search(search_text, 0, None)
        if found:
            match_start, match_end = found
            buffer.select_range(match_start, match_end)
            editor._view.scroll_to_mark(buffer.get_insert(), 0.25, True, 0.5, 0.5)
    
    def _on_replace(self, widget) -> None:
        """Replace current occurrence."""
        if not self._current_document:
            return
        
        search_text = self._find_entry.get_text()
        replace_text = self._replace_entry.get_text()
        
        if not search_text:
            return
        
        # Get current editor
        page = self._editor_notebook.get_current_page()
        editor = self._editor_notebook.get_nth_page(page)
        if not editor or not hasattr(editor, '_buffer'):
            return
        
        buffer = editor._buffer
        
        # Check if there's a selection
        if buffer.get_has_selection():
            start, end = buffer.get_selection_bounds()
            selected = buffer.get_text(start, end, True)
            if selected == search_text:
                buffer.delete(start, end)
                buffer.insert(start, replace_text)
                # Find next
                self._on_find_next(widget)
    
    def _on_replace_all(self, widget) -> None:
        """Replace all occurrences."""
        if not self._current_document:
            return
        
        search_text = self._find_entry.get_text()
        replace_text = self._replace_entry.get_text()
        
        if not search_text:
            return
        
        # Use document's replace method
        count = 0
        pos = 0
        while True:
            new_pos = self._current_document.replace(search_text, replace_text, pos)
            if new_pos == -1:
                break
            count += 1
            pos = new_pos + len(replace_text)
        
        # Reload editor content
        page = self._editor_notebook.get_current_page()
        editor = self._editor_notebook.get_nth_page(page)
        if editor and hasattr(editor, '_buffer'):
            editor._buffer.set_text(self._current_document.content)
        
        self._show_info(f"Replaced {count} occurrences")
    
    def _on_goto_line(self, widget) -> None:
        """Handle goto line request."""
        if not self._current_document:
            return
        
        page = self._editor_notebook.get_current_page()
        editor = self._editor_notebook.get_nth_page(page)
        if not editor or not hasattr(editor, '_buffer'):
            return
        
        # Get total line count
        buffer = editor._buffer
        total_lines = buffer.get_line_count()
        
        # Create dialog
        dialog = Gtk.Dialog(title="Goto Line", transient_for=self, modal=True)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Go", Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        dialog.set_default_size(250, 100)
        
        content = dialog.get_content_area()
        content.set_spacing(6)
        content.set_border_width(12)
        
        label = Gtk.Label(label=f"Enter line number (1-{total_lines}):")
        content.add(label)
        
        spin = Gtk.SpinButton.new_with_range(1, total_lines, 1)
        spin.set_numeric(True)
        # Set current line as default
        cursor_iter = buffer.get_iter_at_mark(buffer.get_insert())
        current_line = cursor_iter.get_line() + 1
        spin.set_value(current_line)
        content.add(spin)
        
        content.show_all()
        spin.grab_focus()
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            line_num = int(spin.get_value()) - 1  # 0-indexed
            editor.goto_line(line_num, 0)
        
        dialog.destroy()
    
    def _on_toggle_line_numbers(self, widget) -> None:
        """Handle line numbers toggle."""
        page = self._editor_notebook.get_current_page()
        editor = self._editor_notebook.get_nth_page(page)
        if not editor or not hasattr(editor, '_view'):
            return
        
        # Toggle line numbers visibility
        current = editor._view.get_show_line_numbers()
        editor._view.set_show_line_numbers(not current)
    
    def _on_regex_toolkit(self, widget) -> None:
        """Handle regex toolkit request."""
        dialog = Gtk.Dialog(title="Regex Toolkit", transient_for=self, modal=False)
        dialog.set_default_size(500, 400)
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        
        content = dialog.get_content_area()
        content.set_spacing(6)
        content.set_border_width(12)
        
        # Pattern entry
        pattern_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        pattern_box.add(Gtk.Label(label="Pattern:"))
        pattern_entry = Gtk.Entry()
        pattern_entry.set_placeholder_text("Enter regex pattern...")
        pattern_box.pack_start(pattern_entry, True, True, 0)
        content.add(pattern_box)
        
        # Test text view
        content.add(Gtk.Label(label="Test Text:"))
        test_scroll = Gtk.ScrolledWindow()
        test_scroll.set_size_request(-1, 120)
        test_buffer = Gtk.TextBuffer()
        test_view = Gtk.TextView.new_with_buffer(test_buffer)
        test_scroll.add(test_view)
        content.add(test_scroll)
        
        # Result label
        result_label = Gtk.Label(label="Enter pattern and test text")
        result_label.set_line_wrap(True)
        content.add(result_label)
        
        # Matches list
        content.add(Gtk.Label(label="Matches:"))
        matches_store = Gtk.ListStore(str, str)
        matches_tree = Gtk.TreeView(model=matches_store)
        matches_tree.append_column(Gtk.TreeViewColumn("Position", Gtk.CellRendererText(), text=0))
        matches_tree.append_column(Gtk.TreeViewColumn("Match", Gtk.CellRendererText(), text=1))
        matches_scroll = Gtk.ScrolledWindow()
        matches_scroll.set_size_request(-1, 100)
        matches_scroll.add(matches_tree)
        content.add(matches_scroll)
        
        def on_pattern_changed(*args):
            pattern = pattern_entry.get_text()
            test_text = test_buffer.get_text(
                test_buffer.get_start_iter(),
                test_buffer.get_end_iter(),
                False
            )
            matches_store.clear()
            
            if not pattern or not test_text:
                result_label.set_text("Enter pattern and test text")
                return
            
            try:
                import re
                regex = re.compile(pattern)
                matches = list(regex.finditer(test_text))
                
                if matches:
                    result_label.set_text(f"Found {len(matches)} match(es)")
                    for m in matches:
                        matches_store.append([f"{m.start()}-{m.end()}", m.group()])
                else:
                    result_label.set_text("No matches found")
            except re.error as e:
                result_label.set_text(f"Invalid regex: {e}")
        
        pattern_entry.connect("changed", on_pattern_changed)
        test_buffer.connect("changed", on_pattern_changed)
        
        content.show_all()
        dialog.run()
        dialog.destroy()
    
    def _on_word_count(self, widget) -> None:
        """Handle word count request."""
        if self._current_document:
            wc = self._current_document.word_count
            lines = self._current_document.line_count
            chars = self._current_document.char_count
            self._show_info(f"Words: {wc}\nLines: {lines}\nCharacters: {chars}")
    
    def _on_about(self, widget) -> None:
        """Handle about request."""
        dialog = Gtk.AboutDialog(transient_for=self)
        dialog.set_program_name("helloed")
        dialog.set_version("8.0.0")
        dialog.set_copyright("Copyright © 2026 Ahmed Youssef")
        dialog.set_license_type(Gtk.License.GPL_2_0)
        dialog.set_website("https://github.com/xmonader/helloed")
        dialog.set_comments("A Python 3/GTK3 text editor with syntax highlighting")
        dialog.run()
        dialog.destroy()
    
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
            # Ctrl+F: Find
            elif event.keyval == Gdk.KEY_f:
                self._show_find_replace_dialog()
                return True
            # Ctrl+G: Goto Line
            elif event.keyval == Gdk.KEY_g:
                self._on_goto_line(widget)
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
    
    def _show_info(self, message: str) -> None:
        """Show info dialog."""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
    
    @property
    def current_document(self) -> Optional[Document]:
        """Get current document."""
        return self._current_document
