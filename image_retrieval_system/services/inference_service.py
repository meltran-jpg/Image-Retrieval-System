from ..events import IMAGE_SUBMITTED, INFERENCE_COMPLETED, make_event
from ..broker import MessageBroker


class InferenceService:
    # listens for image submissions and publishes simulated inference results

    def __init__(self, broker: MessageBroker)-> None:
        self.broker = broker
        # track processed event ids to enforce idempotency
        self._processed_events: set[str] = set()
        self.broker.subscribe(IMAGE_SUBMITTED, self.handle_image_submitted)



    async def handle_image_submitted(self, event) -> None:
        #ignore duplicate image submission events
        if event.event_id in self._processed_events:
            return
        self._processed_events.add(event.event_id)
        image_id = event.payload.get("image_id")
        annotations = self._mock_annotations(image_id)
        output = {"image_id": image_id,"annotations": annotations, "metadata": {"source_path": event.payload.get("path")},}
        # publish the completed inference event for downstream services
        await self.broker.publish(make_event(INFERENCE_COMPLETED, output))






    def _mock_annotations(self, image_id: str | None) -> list[dict[str, object]]:
        #generate deterministic mock object detections based on the image id
        if image_id and image_id.endswith("002"):
            return [{"label":"vehicle", "bbox":[10, 20, 100, 80],"confidence": 0.88},{"label": "wheel","bbox": [45, 50, 70, 90], "confidence": 0.95}]
        return [{"label": "person", "bbox": [5, 15, 50, 120], "confidence": 0.92},{"label": "tree", "bbox": [120, 10, 240, 300], "confidence": 0.81},]
