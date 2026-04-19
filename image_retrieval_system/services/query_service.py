from ..databases import VectorDatabase
from ..events import make_event
from ..broker import MessageBroker


class QueryService:
    #  handles user search queries by performing vector similarity search

    def __init__(self, broker: MessageBroker, vector_db: VectorDatabase |None = None)-> None:
        self.broker = broker
        self.vector_db = vector_db or VectorDatabase()
        self._processed_events: set[str] = set()
        self.broker.subscribe("query.submitted", self.handle_query_submitted)

    async def handle_query_submitted(self, event) -> None:
        # ignore duplicate queries and preserve event order tolerance
        if event.event_id in self._processed_events:
            return
        self._processed_events.add(event.event_id)
        query_text = event.payload.get("query", "")
        top_k = int(event.payload.get("top_k", 3))
        query_vector = self._mock_query_embedding(query_text)
        results = self.vector_db.search(query_vector, top_k=top_k)
        payload = {"query": query_text,"results": [{"image_id": image_id, "score": score} for image_id, score in results]}
        await self.broker.publish(make_event("query.completed", payload))
    def _mock_query_embedding(self, query_text: str) -> list[float]:
        #convert text queries into a simple numeric representation
        length= len(query_text)
        return [float(length + i)/10.0 for i in range(1, 5)]
