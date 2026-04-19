




from ..events import make_event
from ..broker import MessageBroker




class CLIService:
    #simulates user interactions and publishes cli events to the broker
    def __init__(self, broker: MessageBroker)-> None:
        # the cli only talks to the broker, never directly to other services
        self.broker = broker
    async def submit_image(self, image_id: str, path: str) -> None:
        #publish a new image upload event to trigger downstream processing
        event= make_event("image.submitted",{"image_id": image_id, "path": path})
        await self.broker.publish(event)
    async def submit_query(self, query_text: str, top_k: int = 3) -> None:
        #publish a search query event to the broker
        event = make_event("query.submitted", {"query": query_text, "top_k": top_k})
        await self.broker.publish(event)
    async def run_simulation(self)-> None:
        #imulated user workflow for cli interactions
        await self.submit_image("img-001", "/data/images/img-001.jpg")
        await self.submit_image("img-002", "/data/images/img-002.jpg")
        await self.submit_query("red object")
