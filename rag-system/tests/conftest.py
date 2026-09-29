import hashlib
import os
import sys
import types
from types import SimpleNamespace

import numpy as np
import pytest
from qdrant_client import QdrantClient


# ---------------------------------------------------
# Stub heavy dependencies before any app module is imported.
# The app loads SentenceTransformer / CrossEncoder models and an
# OpenAI client at import time; tests must not download models
# or require an API key.
# ---------------------------------------------------

EMBEDDING_DIM = 32


def _embed(text: str) -> np.ndarray:
    # Deterministic bag-of-words vector: texts sharing words are similar
    vector = np.zeros(EMBEDDING_DIM, dtype="float32")
    for word in text.lower().split():
        bucket = int(hashlib.md5(word.encode()).hexdigest(), 16) % EMBEDDING_DIM
        vector[bucket] += 1.0
    norm = np.linalg.norm(vector)
    return vector / norm if norm else vector


class FakeSentenceTransformer:

    def __init__(self, *args, **kwargs):
        pass

    def encode(self, sentences, normalize_embeddings=False):
        if isinstance(sentences, str):
            return _embed(sentences)
        return np.array([_embed(s) for s in sentences])


class FakeCrossEncoder:

    def __init__(self, *args, **kwargs):
        pass

    def predict(self, pairs):
        # Score = number of words shared between query and passage
        return np.array([
            float(len(set(q.lower().split()) & set(p.lower().split())))
            for q, p in pairs
        ])


fake_sentence_transformers = types.ModuleType("sentence_transformers")
fake_sentence_transformers.SentenceTransformer = FakeSentenceTransformer
fake_sentence_transformers.CrossEncoder = FakeCrossEncoder
sys.modules["sentence_transformers"] = fake_sentence_transformers

os.environ.setdefault("OPENAI_API_KEY", "test-key")


# ---------------------------------------------------
# Fixtures
# ---------------------------------------------------

class FakeOpenAIClient:
    """Records chat.completions.create calls and returns a canned reply."""

    def __init__(self, reply: str = "stub answer"):
        self.reply = reply
        self.calls = []
        self.chat = SimpleNamespace(
            completions=SimpleNamespace(create=self._create)
        )

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(content=self.reply)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


@pytest.fixture
def fake_openai(monkeypatch):
    from app.api import analyze
    from app.llm import openai_service

    fake = FakeOpenAIClient()
    monkeypatch.setattr(openai_service, "client", fake)
    monkeypatch.setattr(analyze, "client", fake)
    return fake


@pytest.fixture
def qdrant(monkeypatch):
    from app.vector_store import qdrant_store

    client = QdrantClient(":memory:")
    monkeypatch.setattr(qdrant_store, "client", client)
    yield client
    client.close()


@pytest.fixture
def api_client(tmp_path, monkeypatch, qdrant, fake_openai):
    from fastapi.testclient import TestClient

    from app.api import upload
    from app.main import app

    monkeypatch.setattr(upload, "UPLOAD_DIR", str(tmp_path))
    return TestClient(app)
