


from ..databases import DocumentDatabase
from ..events import ANNOTATION_STORED, INFERENCE_COMPLETED, make_event
from ..broker import MessageBroker

# 

class AnnotationService:
    #transforms inference output into stored annotation documents
    def __init__(self, broker: MessageBroker, document_db: DocumentDatabase | None = None) -> None:
        self.broker = broker
        # use a dedicated document database instance unless one is injected.
        self.document_db = document_db or DocumentDatabase()
        self._processed_events: set[str] = set()
        self.broker.subscribe(INFERENCE_COMPLETED, self.handle_inference_completed)

    async def handle_inference_completed(self, event) -> None:
        # ignore duplicates and preserve eventual consistency.
        if event.event_id in self._processed_events:
            return
        self._processed_events.add(event.event_id)
        payload = event.payload
        record = {"image_id": payload["image_id"],"detected_objects": payload["annotations"], "metadata": payload.get("metadata", {}),"review_history": []}
        # store the annotation and publish a follow-up event only when new.
        stored = await self.document_db.save_annotation(record)
        if stored:
            await self.broker.publish(make_event(ANNOTATION_STORED,{"image_id": record["image_id"], "record": record}))
