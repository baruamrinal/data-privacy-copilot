from fastapi import APIRouter
from pydantic import BaseModel

from sentence_transformers import CrossEncoder

from app.embeddings.embedding_service import model
from app.vector_store.qdrant_store import search_similar
from app.llm.openai_service import generate_compliance_answer

router = APIRouter()


# ---------------------------------------------------
# Request Model
# ---------------------------------------------------

class QueryRequest(BaseModel):
    question: str


# ---------------------------------------------------
# Cross Encoder Reranker
# ---------------------------------------------------

reranker = CrossEncoder("BAAI/bge-reranker-large")


# ---------------------------------------------------
# Query Expansion Dictionary
# ---------------------------------------------------

QUERY_EXPANSIONS = {
    "pii": [
        "personal data",
        "personally identifiable information",
        "customer data",
        "user information",
        "identifiers",
        "ip addresses",
        "device information",
        "email address"
    ],

    "email": [
        "email address",
        "customer email",
        "user email",
        "contact information"
    ],

    "gdpr": [
        "general data protection regulation",
        "EU privacy law"
    ],

    "cross-border": [
        "international transfer",
        "data transfer",
        "transfer outside EEA",
        "standard contractual clauses",
        "SCC"
    ],

    "retention": [
        "data retention",
        "storage duration",
        "deletion",
        "data lifecycle"
    ]
}


# ---------------------------------------------------
# Query Expansion Function
# ---------------------------------------------------

def expand_query(question: str):

    expanded = question.lower()

    for keyword, synonyms in QUERY_EXPANSIONS.items():

        if keyword in expanded:
            expanded += " " + " ".join(synonyms)

    return expanded


# ---------------------------------------------------
# Query API
# ---------------------------------------------------

@router.post("/query")
async def query_documents(request: QueryRequest):

    # ------------------------------------------------
    # Expand Query
    # ------------------------------------------------

    expanded_query = expand_query(request.question)

    retrieval_query = (
        f"Represent this legal compliance query for retrieval: "
        f"{expanded_query}"
    )

    # ------------------------------------------------
    # Generate Query Embedding
    # ------------------------------------------------

    query_embedding = model.encode(
        retrieval_query,
        normalize_embeddings=True
    )

    # ------------------------------------------------
    # Retrieve Candidate Chunks
    # ------------------------------------------------

    results = search_similar(
        query_embedding,
        top_k=10
    )

    # ------------------------------------------------
    # Handle No Results
    # ------------------------------------------------

    if not results:

        return {
            "question": request.question,
            "answer": "No relevant clauses found.",
            "matches": []
        }

    # ------------------------------------------------
    # Rerank Results
    # ------------------------------------------------

    pairs = [
        (request.question, r["text"])
        for r in results
    ]

    rerank_scores = reranker.predict(pairs)

    for idx, score in enumerate(rerank_scores):

        results[idx]["rerank_score"] = float(score)

    # ------------------------------------------------
    # Sort By Rerank Score
    # ------------------------------------------------

    results = sorted(
        results,
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    # ------------------------------------------------
    # Keep Top Results
    # ------------------------------------------------

    results = results[:3]

    # ------------------------------------------------
    # Generate GPT-4.1 Answer
    # ------------------------------------------------

    answer = generate_compliance_answer(
        request.question,
        results
    )

    # ------------------------------------------------
    # Final Response
    # ------------------------------------------------

    return {
        "question": request.question,
        "expanded_query": expanded_query,
        "answer": answer,
        "total_matches": len(results),
        "matches": [
            {
                "vector_score": round(r["score"], 3),
                "rerank_score": round(r["rerank_score"], 3),
                "document": r["metadata"].get("filename"),
                "text": r["text"][:1200]
            }
            for r in results
        ]
    }