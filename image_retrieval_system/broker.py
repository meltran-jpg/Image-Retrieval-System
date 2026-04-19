


# simpl broker for the eventdriven architecture
# services communicate only through events published to the broker
import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine

from .events import Event, validate_event

CallbackType = Callable[[Event], Coroutine[Any, Any, None]]


class MessageBroker:
    #dispatches events to subscribed service callbacks

    def __init__(self) -> None:
        # mapping from topic names to subscriber callback lists
        self.subscribers: dict[str, list[CallbackType]] = defaultdict(list)
        self.queue: asyncio.Queue[Event] = asyncio.Queue()
        self._running = False
        self._dispatch_task: asyncio.Task | None = None




    def subscribe(self, topic: str, callback: CallbackType) -> None:
        # register a service callback to receive events for a topic
        self.subscribers[topic].append(callback)






    async def publish(self, event: Event) -> None:
        #validate and queue events from services. invalid events are ignored
        if not validate_event(event):
            print("broker: invalid event ignored", event)
            return
        await self.queue.put(event)

    async def start(self) -> None:
        # start the dispatch loop if not already running
        if self._running:
            return
        self._running = True
        self._dispatch_task = asyncio.create_task(self._dispatch_loop())

    async def stop(self) -> None:
        # stop dispatching events and cancel the background task
        self._running = False
        if self._dispatch_task:
            self._dispatch_task.cancel()
            try:
                await self._dispatch_task
            except asyncio.CancelledError:
                pass

    async def _dispatch_loop(self) -> None:
        # continuously pull events off the queue and route them to subscribers
        while self._running:
            event = await self.queue.get()
            subscribers = list(self.subscribers.get(event.topic, []))
            for callback in subscribers:
                asyncio.create_task(self._dispatch_to_subscriber(callback, event))

    async def _dispatch_to_subscriber(self, callback: CallbackType, event: Event) -> None:
        # deliver one event to a single subscriber and handle failures
        try:
            await callback(event)
        except Exception as exc:
            print(f"broker error dispatching {event.topic}: {exc}")
