# app/vector_store/qdrant_store.py

from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

import uuid


# -----------------------------
# Qdrant Configuration
# -----------------------------

COLLECTION_NAME = "privacy_compliance_docs"

client = QdrantClient(
    host="localhost",
    port=6333
)


# -----------------------------
# Create Collection
# -----------------------------

def create_collection(vector_size: int):

    existing_collections = client.get_collections().collections

    collection_names = [c.name for c in existing_collections]

    if COLLECTION_NAME not in collection_names:

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        print(f"Collection created: {COLLECTION_NAME}")

    else:
        print(f"Collection already exists: {COLLECTION_NAME}")


# -----------------------------
# Store Embeddings
# -----------------------------

def store_embeddings(chunks, embeddings, metadata=None):

    if metadata is None:
        metadata = {}

    vector_size = len(embeddings[0])

    create_collection(vector_size)

    points = []

    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding.tolist(),
            payload={
                "text": chunk,
                "chunk_id": idx,
                **metadata
            }
        )

        points.append(point)

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )

    return {
        "vectors_stored": len(points)
    }


# -----------------------------
# Semantic Search
# -----------------------------

def search_similar(query_embedding, top_k=3):

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding.tolist(),
        limit=top_k
    ).points

    retrieved_chunks = []

    for result in results:

        retrieved_chunks.append({
            "score": result.score,
            "text": result.payload["text"],
            "metadata": result.payload
        })

    return retrieved_chunks