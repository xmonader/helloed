"""Configuration management for helloed."""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Any
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class EditorConfig:
    """Editor configuration settings."""
    font_family: str = "Monospace"
    font_size: int = 10
    tab_width: int = 4
    use_spaces: bool = True
    show_line_numbers: bool = True
    show_whitespace: bool = False
    highlight_current_line: bool = True
    auto_indent: bool = True
    word_wrap: bool = False
    theme: str = "classic"


@dataclass
class WindowConfig:
    """Window configuration settings."""
    width: int = 900
    height: int = 700
    maximized: bool = False
    sidebar_visible: bool = True
    bottom_panel_visible: bool = True


@dataclass
class AppConfig:
    """Main application configuration."""
    editor: EditorConfig = field(default_factory=EditorConfig)
    window: WindowConfig = field(default_factory=WindowConfig)
    recent_files: List[str] = field(default_factory=list)
    recent_files_limit: int = 10
    auto_save: bool = False
    auto_save_interval: int = 300  # seconds
    backup_files: bool = True
    default_encoding: str = "utf-8"


class ConfigManager:
    """Manages application configuration.
    
    Provides loading, saving, and access to configuration settings.
    Configuration is stored as JSON in ~/.config/helloed/config.json
    """
    
    _instance: Optional['ConfigManager'] = None
    
    def __new__(cls) -> 'ConfigManager':
        """Singleton pattern for ConfigManager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize configuration manager."""
        if self._initialized:
            return
            
        self._config_dir = Path.home() / ".config" / "helloed"
        self._config_file = self._config_dir / "config.json"
        self._config = AppConfig()
        
        self._initialized = True
        self.load()
    
    @property
    def config(self) -> AppConfig:
        """Get the current configuration."""
        return self._config
    
    @property
    def config_dir(self) -> Path:
        """Get configuration directory path."""
        return self._config_dir
    
    def load(self) -> None:
        """Load configuration from file."""
        if not self._config_file.exists():
            logger.info("Config file not found, using defaults")
            return
        
        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._update_from_dict(data)
            logger.debug("Configuration loaded from %s", self._config_file)
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse config file: %s", e)
        except Exception as e:
            logger.error("Failed to load config: %s", e)
    
    def save(self) -> None:
        """Save configuration to file."""
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self._config), f, indent=2)
            
            logger.debug("Configuration saved to %s", self._config_file)
            
        except Exception as e:
            logger.error("Failed to save config: %s", e)
    
    def _update_from_dict(self, data: dict) -> None:
        """Update config from dictionary."""
        # Update editor config
        if 'editor' in data:
            editor_data = data['editor']
            for key, value in editor_data.items():
                if hasattr(self._config.editor, key):
                    setattr(self._config.editor, key, value)
        
        # Update window config
        if 'window' in data:
            window_data = data['window']
            for key, value in window_data.items():
                if hasattr(self._config.window, key):
                    setattr(self._config.window, key, value)
        
        # Update app-level settings
        for key in ['recent_files', 'recent_files_limit', 'auto_save',
                    'auto_save_interval', 'backup_files', 'default_encoding']:
            if key in data:
                setattr(self._config, key, data[key])
    
    def add_recent_file(self, filepath: str) -> None:
        """Add a file to recent files list.
        
        Args:
            filepath: Path to the file
        """
        # Remove if already exists to move to front
        if filepath in self._config.recent_files:
            self._config.recent_files.remove(filepath)
        
        # Add to front
        self._config.recent_files.insert(0, filepath)
        
        # Trim to limit
        self._config.recent_files = self._config.recent_files[
            :self._config.recent_files_limit
        ]
        
        self.save()
    
    def get_recent_files(self) -> List[str]:
        """Get list of recent files that still exist."""
        valid_files = []
        for filepath in self._config.recent_files:
            if Path(filepath).exists():
                valid_files.append(filepath)
        
        # Update if some files were removed
        if len(valid_files) != len(self._config.recent_files):
            self._config.recent_files = valid_files
            self.save()
        
        return valid_files
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self._config = AppConfig()
        self.save()
        logger.info("Configuration reset to defaults")
