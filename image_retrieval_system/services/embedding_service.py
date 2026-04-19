from ..databases import VectorDatabase
from ..events import make_event
from ..broker import MessageBroker



class EmbeddingService:
    # creates vector embeddings from annotation records and indexs them


    def __init__(self, broker: MessageBroker,vector_db: VectorDatabase| None = None)-> None:
        self.broker = broker
        self.vector_db = vector_db or VectorDatabase()
        self._processed_events: set[str] = set()
        self.broker.subscribe("annotation.stored", self.handle_annotation_stored)
    async def handle_annotation_stored(self, event) -> None:
        # ensure duplicate stored events do not create duplicate embeddings
        if event.event_id in self._processed_events:
            return
        self._processed_events.add(event.event_id)
        image_id = event.payload["image_id"]
        record =event.payload[ "record"]
        vector = self._mock_embedding(image_id, record)
        created = await self.vector_db.index(image_id, vector)
        if created:
            await self.broker.publish(make_event("embedding.created", {"image_id": image_id, "vector": vector}))
    def _mock_embedding(self, image_id: str, record: dict[str, object]) -> list[float]:
        #build a simple deterministic embedding based on object count
        base= len(record.get("detected_objects", []))
        return [float(base + i) / 10.0 for i in range(1, 5)]
