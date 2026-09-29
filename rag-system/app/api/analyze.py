import json
from fastapi import APIRouter
from pydantic import BaseModel

from app.embeddings.embedding_service import model
from app.vector_store.qdrant_store import search_similar
from app.llm.openai_service import client

router = APIRouter()


class AnalyzeRequest(BaseModel):
    question: str


@router.post("/analyze")
async def analyze_document(request: AnalyzeRequest):

    query_embedding = model.encode(
        request.question,
        normalize_embeddings=True
    )

    results = search_similar(
        query_embedding,
        top_k=15
    )

    context = "\n\n".join([
        r["text"]
        for r in results
    ])

    prompt = f"""
You are an enterprise AI Privacy and Compliance Copilot.

Analyze the document context below and extract structured compliance intelligence.

Document Context:
{context}

Return JSON only with this structure:

{{
  "processes_personal_data": true/false,
  "personal_data_categories": [],
  "cross_border_transfer": true/false,
  "retention_clause_present": true/false,
  "security_obligations_present": true/false,
  "subprocessors_allowed": true/false,
  "gdpr_applicable": true/false,
  "risk_level": "Low | Medium | High",
  "summary": ""
}}

Be legally cautious.
Do not hallucinate.
Only use evidence from the document.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.1,
        messages=[
            {
                "role": "system",
                "content": "You are a compliance AI system."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    analysis_text = response.choices[0].message.content

    try:

        analysis_json = json.loads(analysis_text)

    except Exception:

        analysis_json = {
            "error": "Failed to parse LLM response",
            "raw_response": analysis_text
        }

    return {
        "analysis": analysis_json
    }