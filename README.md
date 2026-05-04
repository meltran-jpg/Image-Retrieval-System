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

## Optional Redis broker support
The repository includes optional `RedisBroker` support for Pub/Sub event delivery.

Install the Redis Python client before using Redis mode:

```bash
pip install redis
```

Run the demo with Redis enabled:

```bash
USE_REDIS_BROKER=true python main.py
```

To use a custom Redis URL:

```bash
REDIS_URL="redis://localhost:6379" USE_REDIS_BROKER=true python main.py
```

## Optional MongoDB document database support
The repository includes optional `MongoDocumentDatabase` support for storing annotation documents.

Install the MongoDB driver before using MongoDB mode:

```bash
pip install pymongo
```

Run the demo with MongoDB enabled:

```bash
USE_MONGO_DB=true python main.py
```

To use a custom Mongo URI:

```bash
MONGO_DB_URI="mongodb://localhost:27017" USE_MONGO_DB=true python main.py
```

## Optional FAISS vector database support
The repository includes optional `FaissVectorDatabase` support for storing and searching embedding vectors.

Install FAISS before using FAISS mode:

```bash
pip install faiss-cpu numpy
```

Run the demo with FAISS enabled:

```bash
USE_FAISS_DB=true python main.py
```
