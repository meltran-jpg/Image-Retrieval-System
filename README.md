# Event Driven Image Annotation and Retrieval System By Melinda 

repository contains a simple event driven prototype for an image annotation and retrieval system

the architecture is modular and serviceoriented, with services communicating only through a message broker

## Components of Image Annotation
--> `image_retrieval_system/broker.py`: in-memory publish subscribe broker
-->  `image_retrieval_system/events.py`: event schema and helper functions
--> `image_retrieval_system/databases.py`: simple document and vector store implementations
--> `image_retrieval_system/services/`: service modules for the CLI, inference, annotation, embedding,  and query processing
-->  `main.py`: orchestration and demonstration of the event flow
--> `tests/test_event_flow.py`: basic validation of idempotency and event handling

## running the demo
From the project root:
python main.py

## running the tests
python -m unittest discover -s tests


## Design notes
-->  All services publish and subscribe to events through the broker
-->  The CLI never accesses databases directly
-->  Duplicate events are ignored by each service using event IDs
-->  Bad events are ignored by the broker
-->  The vector database supports nearest neighbor search using cosine similarity (learned in ml class)

## Optional Mongo (MG) database support
The repository now includes optional `MongoDocumentDatabase` and `MongoVectorDatabase` implementations in `image_retrieval_system/databases.py`.

Install the MongoDB driver before using MG mode:

```bash
pip install pymongo
```

Run the demo with Mongo/MG enabled:

```bash
USE_MG_DB=true python main.py
```

To use a custom Mongo URI:

```bash
MG_DB_URI="mongodb://localhost:27017" USE_MG_DB=true python main.py
```
