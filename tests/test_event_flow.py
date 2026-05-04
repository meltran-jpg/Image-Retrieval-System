




# tests/test_event_flow.py
# unit tests for the event flow and interactions between services in the image retrieval  system


# imports 
import unittest
from image_retrieval_system.broker import MessageBroker
from image_retrieval_system.databases import FaissVectorDatabase, VectorDatabase, faiss
from image_retrieval_system.events import make_event
from image_retrieval_system.services.annotation_service import AnnotationService
from image_retrieval_system.services.query_service import QueryService

# fake broker to test event flow without the full async infrastructure
class FakeBroker:
    def __init__(self)-> None:
        self.subscribers: dict[str, list] = {}
    def subscribe(self, topic: str, callback) -> None:
        self.subscribers.setdefault(topic, []).append(callback)
    async def publish(self, event) -> None:
        callbacks = self.subscribers.get(event.topic, [])
        for callback in callbacks:
            await callback(event)

# test cases for event flow and service interactions
class EventFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_duplicate_inference_does_not_duplicate_annotation(self)  -> None:
        fake_broker = FakeBroker()
        annotation_service = AnnotationService(fake_broker)
        event = make_event(



            # simulate an inference completed event with the same image id and record to test
            "inference.completed",
            {
                "image_id": "img-100",
                "annotations": [{"label": "person", "bbox": [0, 0, 10, 10], "confidence": 0.9}],
                "metadata": {"source_path": "/data/images/img-100.jpg"},
            },


        )

        await fake_broker.publish(event)
        await fake_broker.publish(event)

        self.assertEqual(len(annotation_service.document_db.all_annotations()), 1)
    # test that malformed events do not crash the broker and are safely ignored
    async def test_malformed_event_does_not_crash_broker(self) -> None:
        broker = MessageBroker()
        await broker.start()
        await broker.publish("not-an-event")
        await broker.stop()
        self.assertTrue(True)
    # test that the query service correctly processes a submitted query and returns results based on the vector database
    async def test_query_service_returns_best_match(self) -> None:
        fake_broker = FakeBroker()
        vector_db = VectorDatabase()
        await vector_db.index("img-1", [0.1, 0.2, 0.3, 0.4])
        await vector_db.index("img-2", [1.0, 1.0, 1.0, 1.0])
        QueryService(fake_broker, vector_db=vector_db)
        results = []
        # collect the query results for verification
        async def collect(event):
            results.append(event.payload)
        fake_broker.subscribe("query.completed", collect)
        await fake_broker.publish(make_event("query.submitted", {"query": "vehicle", "top_k": 1}))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["results"][0]["image_id"], "img-2")

    @unittest.skipIf(faiss is None, "FAISS is not installed")
    async def test_faiss_vector_database_returns_best_match(self) -> None:
        vector_db = FaissVectorDatabase()
        await vector_db.index("img-1", [1.0, 0.0, 0.0, 0.0])
        await vector_db.index("img-2", [0.0, 1.0, 0.0, 0.0])

        results = vector_db.search([0.0, 1.0, 0.0, 0.0], top_k=1)

        self.assertEqual(results[0][0], "img-2")
