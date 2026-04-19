# event definitions and helpers used by all services and the message broker
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional
import uuid



@dataclass
class Event:
    event_id: str
    topic: str
    timestamp: str
    payload: dict

    def to_dict(self) -> dict:
        # convert the dataclass to a plain dictionary.
        return asdict(self)




# factory function to create new events with validation and defaults
def make_event(topic: str, payload: dict, event_id: Optional[str] = None) -> Event:
    if not isinstance(topic, str):
        raise ValueError("topic must be a string")
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")
    return Event(
        event_id=event_id or str(uuid.uuid4()),
        topic=topic,
        timestamp=datetime.now(timezone.utc).isoformat(),
        payload=payload,
    )

# validate that an object conforms to the expected Event structure
def validate_event(event: object)-> bool:
        # basic checks to ensure the event has the required fields and types
    if not isinstance(event, Event):
        return False
    if not event.event_id or not isinstance(event.event_id, str):
        return False
    if not event.topic or not isinstance(event.topic, str):
        return False
    if not isinstance(event.payload, dict):
        return False
    return True
