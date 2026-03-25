"""Plugin system for helloed.

Provides an extensible plugin architecture.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass

from ..logging_config import get_logger
from ..exceptions import PluginError

logger = get_logger(__name__)


@dataclass
class PluginInfo:
    """Plugin metadata."""
    name: str
    version: str
    description: str
    author: str
    website: str = ""
    requires: List[str] = None
    
    def __post_init__(self):
        if self.requires is None:
            self.requires = []


class Plugin(ABC):
    """Base class for plugins.
    
    All plugins must inherit from this class and implement
    the required methods.
    """
    
    # Plugin metadata - override in subclasses
    INFO = PluginInfo(
        name="unnamed",
        version="0.0.0",
        description="No description",
        author="Unknown",
        website="",
        requires=[]
    )
    
    def __init__(self):
        self._app: Optional[Any] = None
        self._active: bool = False
        self._config: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Get plugin name."""
        return self.INFO.name
    
    @property
    def version(self) -> str:
        """Get plugin version."""
        return self.INFO.version
    
    @property
    def active(self) -> bool:
        """Check if plugin is active."""
        return self._active
    
    @abstractmethod
    def activate(self, app: Any) -> None:
        """Activate the plugin.
        
        Args:
            app: Application instance
        """
        pass
    
    @abstractmethod
    def deactivate(self) -> None:
        """Deactivate the plugin."""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if not set
            
        Returns:
            Configuration value
        """
        return self._config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value
    
    def on_document_opened(self, document: Any) -> None:
        """Called when a document is opened.
        
        Override to handle document open events.
        
        Args:
            document: Document that was opened
        """
        pass
    
    def on_document_closed(self, document: Any) -> None:
        """Called when a document is closed.
        
        Override to handle document close events.
        
        Args:
            document: Document that was closed
        """
        pass
    
    def on_document_saved(self, document: Any) -> None:
        """Called when a document is saved.
        
        Override to handle document save events.
        
        Args:
            document: Document that was saved
        """
        pass


class PluginManager:
    """Manages plugin lifecycle and registration.
    
    Provides a central registry for plugins and manages their
    activation and deactivation.
    """
    
    _instance: Optional['PluginManager'] = None
    
    def __new__(cls) -> 'PluginManager':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize plugin manager."""
        if self._initialized:
            return
            
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_classes: Dict[str, Type[Plugin]] = {}
        self._app: Optional[Any] = None
        self._initialized = True
    
    def set_app(self, app: Any) -> None:
        """Set the application instance."""
        self._app = app
    
    def register(self, plugin_class: Type[Plugin]) -> None:
        """Register a plugin class.
        
        Args:
            plugin_class: Plugin class to register
            
        Raises:
            PluginError: If plugin is already registered or invalid
        """
        if not issubclass(plugin_class, Plugin):
            raise PluginError(f"Class must inherit from Plugin: {plugin_class}")
        
        name = plugin_class.INFO.name
        
        if name in self._plugin_classes:
            raise PluginError(f"Plugin already registered: {name}")
        
        self._plugin_classes[name] = plugin_class
        logger.debug("Registered plugin: %s v%s", name, plugin_class.INFO.version)
    
    def unregister(self, name: str) -> bool:
        """Unregister a plugin.
        
        Args:
            name: Plugin name
            
        Returns:
            True if plugin was unregistered
        """
        if name in self._plugins:
            self.deactivate(name)
        
        if name in self._plugin_classes:
            del self._plugin_classes[name]
            logger.debug("Unregistered plugin: %s", name)
            return True
        
        return False
    
    def activate(self, name: str) -> None:
        """Activate a plugin.
        
        Args:
            name: Plugin name
            
        Raises:
            PluginError: If plugin cannot be activated
        """
        if name in self._plugins:
            logger.debug("Plugin already active: %s", name)
            return
        
        if name not in self._plugin_classes:
            raise PluginError(f"Plugin not found: {name}")
        
        if self._app is None:
            raise PluginError("Application not set, cannot activate plugins")
        
        try:
            plugin_class = self._plugin_classes[name]
            plugin = plugin_class()
            plugin.activate(self._app)
            self._plugins[name] = plugin
            logger.info("Activated plugin: %s v%s", name, plugin.version)
        except Exception as e:
            raise PluginError(f"Failed to activate plugin {name}: {e}", name)
    
    def deactivate(self, name: str) -> None:
        """Deactivate a plugin.
        
        Args:
            name: Plugin name
        """
        if name not in self._plugins:
            return
        
        try:
            plugin = self._plugins[name]
            plugin.deactivate()
            del self._plugins[name]
            logger.info("Deactivated plugin: %s", name)
        except Exception as e:
            logger.error("Error deactivating plugin %s: %s", name, e)
    
    def activate_all(self) -> None:
        """Activate all registered plugins."""
        for name in self._plugin_classes:
            try:
                self.activate(name)
            except PluginError as e:
                logger.error("Failed to activate plugin %s: %s", name, e)
    
    def deactivate_all(self) -> None:
        """Deactivate all active plugins."""
        for name in list(self._plugins.keys()):
            self.deactivate(name)
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get an active plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None
        """
        return self._plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """List all registered plugin names."""
        return list(self._plugin_classes.keys())
    
    def list_active(self) -> List[str]:
        """List all active plugin names."""
        return list(self._plugins.keys())
    
    def get_plugin_info(self, name: str) -> Optional[PluginInfo]:
        """Get plugin metadata.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin info or None
        """
        if name in self._plugin_classes:
            return self._plugin_classes[name].INFO
        return None
    
    def broadcast_event(self, event_name: str, *args, **kwargs) -> None:
        """Broadcast an event to all active plugins.
        
        Args:
            event_name: Name of event method to call
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        for plugin in self._plugins.values():
            if hasattr(plugin, event_name):
                try:
                    method = getattr(plugin, event_name)
                    method(*args, **kwargs)
                except Exception as e:
                    logger.error("Plugin %s failed to handle event %s: %s",
                               plugin.name, event_name, e)


# Global plugin manager instance
plugins = PluginManager()


# Example built-in plugins
class AutoSavePlugin(Plugin):
    """Auto-save plugin example."""
    
    INFO = PluginInfo(
        name="auto_save",
        version="1.0.0",
        description="Automatically saves documents",
        author="helloed Team"
    )
    
    def activate(self, app: Any) -> None:
        self._app = app
        self._timer = None
        self._setup_timer()
        logger.info("AutoSave plugin activated")
    
    def deactivate(self) -> None:
        if self._timer:
            self._timer.stop()
        logger.info("AutoSave plugin deactivated")
    
    def _setup_timer(self) -> None:
        # Would set up GTK timer for auto-save
        pass
    
    def on_document_modified(self, document: Any) -> None:
        # Reset timer on modification
        pass


class WordCountPlugin(Plugin):
    """Word count plugin example."""
    
    INFO = PluginInfo(
        name="word_count",
        version="1.0.0",
        description="Shows word count in status bar",
        author="helloed Team"
    )
    
    def activate(self, app: Any) -> None:
        self._app = app
        logger.info("WordCount plugin activated")
    
    def deactivate(self) -> None:
        logger.info("WordCount plugin deactivated")
    
    def on_document_modified(self, document: Any) -> None:
        # Update word count display
        pass
