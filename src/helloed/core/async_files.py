"""Asynchronous file operations for helloed.

Prevents UI blocking during file I/O operations.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional, Callable, Any
import functools

from ..logging_config import get_logger
from ..exceptions import FileError

logger = get_logger(__name__)


class AsyncFileManager:
    """Manages asynchronous file operations.
    
    Uses a thread pool to perform file I/O without blocking the UI.
    """
    
    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop."""
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_event_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop
    
    async def read_file(self, filepath: Path, encoding: str = "utf-8") -> str:
        """Read file asynchronously.
        
        Args:
            filepath: Path to file
            encoding: File encoding
            
        Returns:
            File content as string
            
        Raises:
            FileError: If file cannot be read
        """
        loop = self._get_loop()
        
        def _read():
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    return f.read()
            except Exception as e:
                raise FileError(f"Failed to read file: {e}", str(filepath))
        
        try:
            content = await loop.run_in_executor(self._executor, _read)
            logger.debug("Async read completed: %s", filepath)
            return content
        except FileError:
            raise
        except Exception as e:
            raise FileError(f"Failed to read file: {e}", str(filepath))
    
    async def write_file(self, filepath: Path, content: str, 
                         encoding: str = "utf-8") -> None:
        """Write file asynchronously.
        
        Args:
            filepath: Path to file
            content: Content to write
            encoding: File encoding
            
        Raises:
            FileError: If file cannot be written
        """
        loop = self._get_loop()
        
        def _write():
            try:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'w', encoding=encoding) as f:
                    f.write(content)
            except Exception as e:
                raise FileError(f"Failed to write file: {e}", str(filepath))
        
        try:
            await loop.run_in_executor(self._executor, _write)
            logger.debug("Async write completed: %s", filepath)
        except FileError:
            raise
        except Exception as e:
            raise FileError(f"Failed to write file: {e}", str(filepath))
    
    async def file_exists(self, filepath: Path) -> bool:
        """Check if file exists asynchronously.
        
        Args:
            filepath: Path to check
            
        Returns:
            True if file exists
        """
        loop = self._get_loop()
        return await loop.run_in_executor(self._executor, filepath.exists)
    
    async def get_file_info(self, filepath: Path) -> dict:
        """Get file information asynchronously.
        
        Args:
            filepath: Path to file
            
        Returns:
            Dictionary with file info
        """
        loop = self._get_loop()
        
        def _get_info():
            stat = filepath.stat()
            return {
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'exists': filepath.exists(),
                'is_file': filepath.is_file(),
                'is_dir': filepath.is_dir(),
            }
        
        return await loop.run_in_executor(self._executor, _get_info)
    
    def run_async(self, coro: Any, callback: Optional[Callable[[Any], None]] = None,
                  error_callback: Optional[Callable[[Exception], None]] = None) -> None:
        """Run coroutine with optional callbacks.
        
        This is a helper method for running async operations from
        synchronous GTK code.
        
        Args:
            coro: Coroutine to run
            callback: Success callback
            error_callback: Error callback
        """
        def _done_callback(future):
            try:
                result = future.result()
                if callback:
                    callback(result)
            except Exception as e:
                logger.exception("Async operation failed")
                if error_callback:
                    error_callback(e)
        
        loop = self._get_loop()
        future = asyncio.ensure_future(coro, loop=loop)
        future.add_done_callback(_done_callback)
    
    def shutdown(self) -> None:
        """Shutdown the thread pool."""
        self._executor.shutdown(wait=True)
        logger.debug("AsyncFileManager shutdown")


# Global instance
_file_manager: Optional[AsyncFileManager] = None


def get_file_manager() -> AsyncFileManager:
    """Get the global file manager instance."""
    global _file_manager
    if _file_manager is None:
        _file_manager = AsyncFileManager()
    return _file_manager
