




# simple in memory databases for annotations and embeddings.
from __future__ import annotations
from math import sqrt
from typing import Any


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
