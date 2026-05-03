




# simple in memory databases for annotations and embeddings.
from __future__ import annotations
from math import sqrt
from typing import Any


try:
    from pymongo import MongoClient
except ImportError:  # pragma: no cover - optional dependency
    MongoClient = None

try:
    import faiss
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency
    faiss = None
    np = None


class DocumentDatabase:
    def __init__(self) -> None:
        #image_id to annotation record
        self._records: dict[str, dict[str, Any]] = {}
    async def save_annotation(self, annotation: dict[str, Any]) -> bool:
        # save or update an annotation record and avoid duplicate writes
        image_id = annotation.get("image_id")
        if not image_id:
            raise ValueError("annotation must include image_id")
        existing = self._records.get(image_id)
        if existing == annotation:
            return False
        self._records[image_id] = annotation
        return True
    def get_annotation(self, image_id: str) -> dict[str, Any] | None:
        # retrieve a saved annotation by image id
        return self._records.get(image_id)
    def all_annotations(self) -> dict[str, dict[str, Any]]:
        # return a shallow copy of all annotation records
        return dict(self._records)


class MongoDocumentDatabase:
    # MongoDB-backed annotation store. Redis is not used for storage.
    def __init__(
        self,
        uri: str = "mongodb://localhost:27017",
        db_name: str = "image_retrieval",
        collection_name: str = "annotations",
    ) -> None:
        if MongoClient is None:
            raise ImportError("Install MongoDB support with: pip install pymongo")

        self.client = MongoClient(uri)
        self.collection = self.client[db_name][collection_name]
        self.collection.create_index("image_id", unique=True)

    async def save_annotation(self, annotation: dict[str, Any]) -> bool:
        image_id = annotation.get("image_id")
        if not image_id:
            raise ValueError("annotation must include image_id")

        existing = self.collection.find_one({"image_id": image_id}, {"_id": 0})
        if existing == annotation:
            return False

        self.collection.update_one(
            {"image_id": image_id},
            {"$set": annotation},
            upsert=True,
        )
        return True

    def get_annotation(self, image_id: str) -> dict[str, Any] | None:
        return self.collection.find_one({"image_id": image_id}, {"_id": 0})

    def all_annotations(self) -> dict[str, dict[str, Any]]:
        records = self.collection.find({}, {"_id": 0})
        return {record["image_id"]: record for record in records}





# simple in memory vector database for storing and searching image
class VectorDatabase:
    def __init__(self) -> None:
        # image_id to0 embedding vector
        self._vectors: dict[str, list[float]] = {}

    async def index(self, image_id: str, vector: list[float]) -> bool:
        # store an embedding vector and prevent duplicate indexing
        if not vector or not isinstance(vector, list):
            raise ValueError("vector must be a non empty list")
        # check if the same vector is already indexed for the image id to avoid duplicates
        existing = self._vectors.get(image_id)
        if existing == vector:
            return False
        # store the new vector for the image id
        self._vectors[image_id] = vector
        return True
    




# perform a vector similarity search and return the top k results with scores
    def search(self, query_vector: list[float], top_k: int = 3) -> list[tuple[str, float]]:
        # return the top k most similar for the query vector 
        if not query_vector or not isinstance(query_vector, list):
            return []

        scored: list[tuple[str, float]] = []
        for image_id, vector in self._vectors.items():
            score = self._cosine_similarity(query_vector, vector)
            scored.append((image_id, score))

        scored.sort(key = lambda item : item[1], reverse= True)
        return scored[:top_k]

#` simple cosine similarity implementation for vector comparison`
    @staticmethod
    # compute cosine similarity between two vectors, returning a score between 0 and 1
    def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
        # simple cosine similarity measure between two equal length vectors
        if len(v1) != len(v2):
            return 0.0
        dot = sum(x * y for x, y in zip(v1, v2))
        norm1 = sqrt(sum(x * x for x in v1))
        norm2 = sqrt(sum(y * y for y in v2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        # cosine similarity is equal to the the dot product divided by the product of the norms
        return dot / (norm1 * norm2)


class FaissVectorDatabase:
    # FAISS-backed vector store for image embeddings.
    def __init__(self) -> None:
        if faiss is None or np is None:
            raise ImportError("Install FAISS support with: pip install faiss-cpu numpy")

        self._index: Any | None = None
        self._image_ids: list[str] = []
        self._vectors: dict[str, list[float]] = {}

    async def index(self, image_id: str, vector: list[float]) -> bool:
        if not image_id:
            raise ValueError("image_id is required")
        if not vector or not isinstance(vector, list):
            raise ValueError("vector must be a non empty list")

        existing = self._vectors.get(image_id)
        if existing == vector:
            return False

        self._vectors[image_id] = vector
        self._rebuild_index()
        return True

    def search(self, query_vector: list[float], top_k: int = 3) -> list[tuple[str, float]]:
        if self._index is None or not query_vector:
            return []

        query = self._as_normalized_array([query_vector])
        scores, positions = self._index.search(query, top_k)

        results: list[tuple[str, float]] = []
        for score, position in zip(scores[0], positions[0]):
            if position == -1:
                continue
            results.append((self._image_ids[position], float(score)))
        return results

    def _rebuild_index(self) -> None:
        self._image_ids = list(self._vectors.keys())
        vectors = self._as_normalized_array(list(self._vectors.values()))
        dimension = vectors.shape[1]
        self._index = faiss.IndexFlatIP(dimension)
        self._index.add(vectors)

    def _as_normalized_array(self, vectors: list[list[float]]) -> Any:
        array = np.array(vectors, dtype="float32")
        faiss.normalize_L2(array)
        return array
