"""CLI entry point for helloed."""

import argparse
import sys
import logging
from pathlib import Path

from . import __version__, setup_logging
from .logging_config import get_logger

logger = get_logger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="helloed",
        description="A Python 3/GTK3 text editor with syntax highlighting",
        epilog="For more information, visit https://github.com/xmonader/helloed"
    )
    
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to open"
    )
    
    parser.add_argument(
        "-l", "--line",
        type=int,
        metavar="N",
        help="Go to line number (1-indexed)"
    )
    
    parser.add_argument(
        "-c", "--column",
        type=int,
        metavar="N",
        help="Go to column number (1-indexed)"
    )
    
    parser.add_argument(
        "-n", "--new-window",
        action="store_true",
        help="Open in new window"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--no-plugins",
        action="store_true",
        help="Disable plugins"
    )
    
    parser.add_argument(
        "--list-plugins",
        action="store_true",
        help="List available plugins and exit"
    )
    
    return parser


def main() -> int:
    """Main entry point.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    
    logger.debug("Starting helloed v%s", __version__)
    logger.debug("Arguments: %s", args)
    
    # Handle plugin listing
    if args.list_plugins:
        from .plugins.base import plugins
        print("Available plugins:")
        for name in plugins.list_plugins():
            info = plugins.get_plugin_info(name)
            print(f"  {name}: {info.description} (v{info.version})")
        return 0
    
    # Import GTK here to avoid slow startup for --help/--version
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
    except ImportError as e:
        logger.error("Failed to import GTK: %s", e)
        print("Error: GTK not available. Please install PyGObject.", file=sys.stderr)
        return 1
    
    # Create and run application
    try:
        from .app import Application
        
        app = Application(
            debug=args.debug,
            disable_plugins=args.no_plugins
        )
        
        # Open specified files
        for filepath in args.files:
            path = Path(filepath).resolve()
            app.open_file(
                path,
                line=args.line,
                column=args.column,
                new_window=args.new_window
            )
        
        # Run the application
        exit_code = app.run()
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as e:
        logger.exception("Fatal error: %s", e)
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
