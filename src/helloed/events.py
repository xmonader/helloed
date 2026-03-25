"""Event system for decoupled component communication.

Implements the Observer pattern for event-driven architecture.
"""

from typing import Callable, Any, List, Dict
from collections import defaultdict
from .logging_config import get_logger
from .exceptions import HelloedError

logger = get_logger(__name__)


class EventBus:
    """Central event bus for application-wide events.
    
    Components can subscribe to events and publish events without
    direct coupling to each other.
    
    Example:
        events = EventBus()
        
        def on_document_change(doc, change_type):
            print(f"Document changed: {change_type}")
        
        events.subscribe("document.changed", on_document_change)
        events.publish("document.changed", doc, change_type="insert")
    """
    
    _instance: 'EventBus' = None
    
    def __new__(cls) -> 'EventBus':
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize event bus."""
        if self._initialized:
            return
            
        self._listeners: Dict[str, List[Callable[..., Any]]] = defaultdict(list)
        self._initialized = True
    
    def subscribe(self, event: str, handler: Callable[..., Any]) -> None:
        """Subscribe to an event.
        
        Args:
            event: Event name
            handler: Callback function to call when event is published
        """
        self._listeners[event].append(handler)
        logger.debug("Subscribed to event '%s': %s", event, handler.__name__)
    
    def unsubscribe(self, event: str, handler: Callable[..., Any]) -> bool:
        """Unsubscribe from an event.
        
        Args:
            event: Event name
            handler: Handler to remove
            
        Returns:
            True if handler was found and removed
        """
        if event in self._listeners and handler in self._listeners[event]:
            self._listeners[event].remove(handler)
            logger.debug("Unsubscribed from event '%s': %s", event, handler.__name__)
            return True
        return False
    
    def publish(self, event: str, *args, **kwargs) -> List[Any]:
        """Publish an event to all subscribers.
        
        Args:
            event: Event name
            *args: Positional arguments to pass to handlers
            **kwargs: Keyword arguments to pass to handlers
            
        Returns:
            List of results from handlers
        """
        results = []
        handlers = self._listeners.get(event, [])
        
        for handler in handlers:
            try:
                result = handler(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.exception("Event handler failed for '%s': %s", event, e)
        
        return results
    
    def publish_sync(self, event: str, *args, **kwargs) -> None:
        """Publish event synchronously, ignoring results.
        
        Args:
            event: Event name
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        self.publish(event, *args, **kwargs)
    
    def clear(self, event: str = None) -> None:
        """Clear all subscribers for an event or all events.
        
        Args:
            event: Event name, or None to clear all
        """
        if event:
            self._listeners[event].clear()
            logger.debug("Cleared all handlers for event '%s'", event)
        else:
            self._listeners.clear()
            logger.debug("Cleared all event handlers")
    
    def get_subscribers(self, event: str) -> List[Callable[..., Any]]:
        """Get list of subscribers for an event.
        
        Args:
            event: Event name
            
        Returns:
            List of subscribed handlers
        """
        return self._listeners.get(event, []).copy()


# Global event bus instance
events = EventBus()


class EventMixin:
    """Mixin class for objects that want event capabilities.
    
    Provides convenience methods for subscribing to and emitting events.
    """
    
    def __init__(self):
        self._event_bus = EventBus()
        self._subscriptions: List[tuple] = []
    
    def emit(self, event: str, *args, **kwargs) -> List[Any]:
        """Emit an event."""
        return self._event_bus.publish(event, *args, **kwargs)
    
    def on(self, event: str, handler: Callable[..., Any]) -> None:
        """Subscribe to an event."""
        self._event_bus.subscribe(event, handler)
        self._subscriptions.append((event, handler))
    
    def off(self, event: str, handler: Callable[..., Any]) -> bool:
        """Unsubscribe from an event."""
        if (event, handler) in self._subscriptions:
            self._subscriptions.remove((event, handler))
        return self._event_bus.unsubscribe(event, handler)
    
    def cleanup_events(self) -> None:
        """Remove all subscriptions for this object."""
        for event, handler in self._subscriptions:
            self._event_bus.unsubscribe(event, handler)
        self._subscriptions.clear()
