
# main.py
# main entry point for the image retrieval system
# sets up the event broker, shared vector database, and all services, then runs a short simulation of the system




import asyncio
import os

from image_retrieval_system.broker import MessageBroker
from image_retrieval_system.databases import (
    DocumentDatabase,
    FaissVectorDatabase,
    MongoDocumentDatabase,
    VectorDatabase,
)
from image_retrieval_system.services.annotation_service import AnnotationService
from image_retrieval_system.services.cli_service import CLIService
from image_retrieval_system.services.embedding_service import EmbeddingService
from image_retrieval_system.services.inference_service import InferenceService
from image_retrieval_system.services.query_service import QueryService


async def result_logger(event) -> None:
    # log completed query results fo r the demonstration purposes
    print("\n[RESULT] query.completed ->", event.payload)


def build_document_db() -> DocumentDatabase | MongoDocumentDatabase:
    # Use MongoDB only for annotation/document storage when requested.
    if os.getenv("USE_MONGO_DB", "").lower() == "true":
        mongo_uri = os.getenv("MONGO_DB_URI", "mongodb://localhost:27017")
        return MongoDocumentDatabase(uri=mongo_uri)
    return DocumentDatabase()


def build_vector_db() -> VectorDatabase | FaissVectorDatabase:
    # Use FAISS only for embedding/vector storage when requested.
    if os.getenv("USE_FAISS_DB", "").lower() == "true":
        return FaissVectorDatabase()
    return VectorDatabase()





async def main()-> None:
    # build the broker and shared vector database for the system
    broker = MessageBroker()
    document_db = build_document_db()
    vector_db = build_vector_db()
    # instantiate services and wire them to the event broker
    InferenceService(broker)
    AnnotationService(broker, document_db=document_db)
    EmbeddingService(broker, vector_db=vector_db)
    QueryService(broker, vector_db=vector_db)
    cli = CLIService(broker)
    broker.subscribe("query.completed", result_logger)
    # start the broker, run a short simulation, then stop cleanly
    await broker.start()
    await cli.run_simulation()
    await asyncio.sleep(0.5)
    await broker.stop()


if __name__ == "__main__":
    asyncio.run(main())
