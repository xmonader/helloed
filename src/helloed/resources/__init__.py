"""Resource management for helloed."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf
from pathlib import Path
from typing import Dict, Optional

from ..logging_config import get_logger

logger = get_logger(__name__)


class ResourceManager:
    """Manages application resources like icons and UI files."""
    
    _instance: Optional['ResourceManager'] = None
    
    def __new__(cls) -> 'ResourceManager':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize resource manager."""
        if self._initialized:
            return
            
        self._icons: Dict[str, GdkPixbuf.Pixbuf] = {}
        self._base_path = Path(__file__).parent
        self._initialized = True
    
    def get_ui_path(self, filename: str) -> Path:
        """Get path to a UI file.
        
        Args:
            filename: UI file name
            
        Returns:
            Path to UI file
        """
        return self._base_path / "ui" / filename
    
    def load_icon(self, name: str, size: int = 16) -> Optional[GdkPixbuf.Pixbuf]:
        """Load an icon.
        
        Args:
            name: Icon name
            size: Icon size in pixels
            
        Returns:
            Loaded icon or None
        """
        cache_key = f"{name}:{size}"
        
        if cache_key in self._icons:
            return self._icons[cache_key]
        
        try:
            icon_theme = Gtk.IconTheme.get_default()
            icon = icon_theme.load_icon(name, size, 0)
            self._icons[cache_key] = icon
            return icon
        except Exception as e:
            logger.warning("Failed to load icon '%s': %s", name, e)
            return None
    
    def clear_cache(self) -> None:
        """Clear icon cache."""
        self._icons.clear()
        logger.debug("Icon cache cleared")


# Global resource manager
resources = ResourceManager()
