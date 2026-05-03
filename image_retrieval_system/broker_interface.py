# Abstract base class for message brokers
# Defines the interface that both in-memory and Redis brokers must implement

from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Any
from .events import Event

CallbackType = Callable[[Event], Coroutine[Any, Any, None]]


class BrokerInterface(ABC):
    """
    Abstract interface for message brokers.
    
    Any broker implementation (in-memory, Redis, etc.) must implement these methods.
    This ensures services work with any broker without code changes.
    """

    @abstractmethod
    def subscribe(self, topic: str, callback: CallbackType) -> None:
        """Register a callback to be invoked when an event is published to this topic."""
        pass

    @abstractmethod
    async def publish(self, event: Event) -> None:
        """Publish an event to be delivered to all subscribers of its topic."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start the broker (begin listening for and processing events)."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the broker gracefully."""
        pass
