import numpy as np
import pytest

from app.embeddings.embedding_service import generate_embeddings
from app.vector_store import faiss_store, qdrant_store


# ---------------------------------------------------
# Qdrant
# ---------------------------------------------------

def test_store_embeddings_creates_collection_and_upserts(qdrant):
    chunks = ["data retention period", "subprocessor list", "security measures"]

    response = qdrant_store.store_embeddings(
        chunks=chunks,
        embeddings=generate_embeddings(chunks),
        metadata={"document_id": "doc-1", "filename": "dpa.pdf"}
    )

    assert response == {"vectors_stored": 3}
    assert qdrant.collection_exists(qdrant_store.COLLECTION_NAME)
    assert qdrant.count(qdrant_store.COLLECTION_NAME).count == 3


def test_create_collection_is_idempotent(qdrant):
    qdrant_store.create_collection(8)
    qdrant_store.create_collection(8)

    assert qdrant.collection_exists(qdrant_store.COLLECTION_NAME)


def test_search_similar_returns_closest_chunk_with_metadata(qdrant):
    chunks = ["data retention period", "subprocessor list", "security measures"]
    qdrant_store.store_embeddings(
        chunks=chunks,
        embeddings=generate_embeddings(chunks),
        metadata={"filename": "dpa.pdf"}
    )

    results = qdrant_store.search_similar(
        generate_embeddings("subprocessor list"),
        top_k=2
    )

    assert len(results) == 2
    top = results[0]
    assert top["text"] == "subprocessor list"
    assert top["score"] == pytest.approx(1.0, abs=1e-5)
    assert top["metadata"]["filename"] == "dpa.pdf"
    assert top["metadata"]["chunk_id"] == 1


# ---------------------------------------------------
# FAISS
# ---------------------------------------------------

@pytest.fixture
def faiss_reset(monkeypatch):
    monkeypatch.setattr(faiss_store, "index", None)
    monkeypatch.setattr(faiss_store, "stored_chunks", [])


def test_faiss_index_and_search(faiss_reset):
    chunks = ["data retention period", "subprocessor list", "security measures"]

    response = faiss_store.create_faiss_index(generate_embeddings(chunks), chunks)

    assert response == {"total_vectors": 3}
    results = faiss_store.search_similar(generate_embeddings("security measures"), top_k=1)
    assert results == ["security measures"]


def test_faiss_accepts_plain_lists(faiss_reset):
    embeddings = [[1.0, 0.0], [0.0, 1.0]]

    faiss_store.create_faiss_index(embeddings, ["a", "b"])

    assert faiss_store.search_similar(np.array([0.1, 0.9]), top_k=2) == ["b", "a"]
