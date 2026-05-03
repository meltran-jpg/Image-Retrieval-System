# Redis-based message broker for distributed event-driven architecture
# Implements BrokerInterface using Redis Pub/Sub for message distribution

from __future__ import annotations
import asyncio
import json
from typing import Callable, Coroutine, Any
import redis.asyncio as redis
from .broker_interface import BrokerInterface
from .events import Event, validate_event

CallbackType = Callable[[Event], Coroutine[Any, Any, None]]


class RedisBroker(BrokerInterface):
    """
    Redis Pub/Sub message broker.
    
    Uses Redis to distribute events across services.
    Services can run on different machines and communicate through Redis.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379") -> None:
        """
        Initialize the Redis broker.
        
        Args:
            redis_url: URL to connect to Redis (default: localhost:6379)
        """
        self.redis_url = redis_url
        self.redis_client: redis.Redis | None = None
        self.pubsub: redis.client.PubSub | None = None
        self.subscribers: dict[str, list[CallbackType]] = {}
        self._subscribed_topics: set[str] = set()
        self._running = False
        self._listener_task: asyncio.Task | None = None

    async def connect(self) -> None:
        """
        Establish connection to Redis.
        
        Raises ConnectionError if Redis is not available.
        """
        if self.redis_client is not None:
            return  # Already connected

        try:
            self.redis_client = await redis.from_url(
                self.redis_url, decode_responses=True
            )
            self.pubsub = self.redis_client.pubsub()
            print(f"✓ Connected to Redis at {self.redis_url}")
        except (ConnectionError, OSError) as e:
            print(f"✗ Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection to Redis gracefully."""
        if self.pubsub is not None:
            await self.pubsub.close()
        if self.redis_client is not None:
            await self.redis_client.close()
        print("✓ Disconnected from Redis")

    def subscribe(self, topic: str, callback: CallbackType) -> None:
        """
        Register a callback for a topic.
        
        When an event is published to this topic, the callback will be invoked.
        Multiple callbacks can subscribe to the same topic.
        
        Args:
            topic: The event topic to subscribe to
            callback: Async function to call when an event arrives
        """
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        print(f"→ Subscribed to topic: {topic}")

    async def publish(self, event: Event) -> None:
        """
        Publish an event to Redis.
        
        Event is validated and serialized to JSON before being sent to Redis.
        Redis will deliver it to all subscribers of that topic.
        
        Args:
            event: Event object to publish
        """
        if not validate_event(event):
            print(f"✗ Invalid event ignored: {event}")
            return

        if self.redis_client is None:
            await self.connect()

        try:
            # Serialize event to JSON
            event_json = json.dumps(event.to_dict())
            # Publish to Redis using topic as channel
            await self.redis_client.publish(event.topic, event_json)
            print(f"→ Published to {event.topic}: {event.event_id}")
        except Exception as e:
            print(f"✗ Error publishing event: {e}")

    async def start(self) -> None:
        """Start Redis Pub/Sub subscriptions and the listener loop."""
        if self._running:
            return

        await self.connect()
        self._running = True

        if self.pubsub is None:
            raise RuntimeError("Redis Pub/Sub connection was not initialized")

        for topic in self.subscribers:
            await self.pubsub.subscribe(topic)
            self._subscribed_topics.add(topic)
            print(f"→ Redis listening on topic: {topic}")

        self._listener_task = asyncio.create_task(self._listen_loop())
        print("✓ Redis broker listener started")

    async def stop(self) -> None:
        """Placeholder - will be implemented in step 2.3"""
        pass

    async def _listen_loop(self) -> None:
        """Keep the Redis Pub/Sub listener alive. Message handling comes next."""
        while self._running:
            await asyncio.sleep(0.1)
