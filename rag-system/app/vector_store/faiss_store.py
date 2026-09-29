import faiss
import numpy as np

index = None
stored_chunks = []


def create_faiss_index(embeddings, chunks):

    global index
    global stored_chunks

    dimension = len(embeddings[0])

    index = faiss.IndexFlatL2(dimension)

    embeddings_np = np.array(embeddings).astype("float32")

    index.add(embeddings_np)

    stored_chunks.extend(chunks)

    return {
        "total_vectors": index.ntotal
    }


def search_similar(query_embedding, top_k=3):

    query_np = np.array([query_embedding]).astype("float32")

    distances, indices = index.search(query_np, top_k)

    results = []

    for idx in indices[0]:
        results.append(stored_chunks[idx])

    return results