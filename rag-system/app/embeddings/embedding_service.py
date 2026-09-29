from sentence_transformers import SentenceTransformer

# Load embedding model once
model = SentenceTransformer("BAAI/bge-large-en-v1.5")


def generate_embeddings(chunks):

    embeddings = model.encode(
        chunks,
        normalize_embeddings=True
    )

    return embeddings