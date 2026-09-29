import json

from app.api.query import expand_query


def _upload_txt(api_client, text, filename="dpa.txt"):
    return api_client.post(
        "/upload-document",
        files={"file": (filename, text.encode("utf-8"), "text/plain")}
    )


# ---------------------------------------------------
# Query expansion
# ---------------------------------------------------

def test_expand_query_adds_synonyms_for_known_keywords():
    expanded = expand_query("Does it cover GDPR retention?")

    assert expanded.startswith("does it cover gdpr retention?")
    assert "general data protection regulation" in expanded
    assert "storage duration" in expanded


def test_expand_query_leaves_unknown_questions_unchanged():
    assert expand_query("Who signs the contract?") == "who signs the contract?"


# ---------------------------------------------------
# Endpoints
# ---------------------------------------------------

def test_health(api_client):
    assert api_client.get("/").json() == {"status": "running"}


def test_upload_indexes_document(api_client, qdrant, tmp_path):
    response = _upload_txt(api_client, "Personal data is retained for 30 days.")

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "dpa.txt"
    assert body["total_chunks"] == 1
    assert body["vectors_stored"] == 1
    assert (tmp_path / f"{body['document_id']}_dpa.txt").exists()
    assert qdrant.count("privacy_compliance_docs").count == 1


def test_query_returns_reranked_matches_and_answer(api_client, fake_openai):
    fake_openai.reply = "Data is retained for 30 days."
    _upload_txt(
        api_client,
        "Personal data is retained for 30 days.\n\n"
        "The processor may engage subprocessors with notice.",
    )

    response = api_client.post("/query", json={"question": "How long is data retained?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Data is retained for 30 days."
    assert body["total_matches"] == len(body["matches"]) >= 1
    assert body["matches"][0]["document"] == "dpa.txt"
    scores = [m["rerank_score"] for m in body["matches"]]
    assert scores == sorted(scores, reverse=True)


def test_query_with_empty_store_returns_no_results(api_client, qdrant, fake_openai):
    qdrant.create_collection(
        "privacy_compliance_docs",
        vectors_config={"size": 32, "distance": "Cosine"}
    )

    response = api_client.post("/query", json={"question": "Anything?"})

    assert response.json()["answer"] == "No relevant clauses found."
    assert fake_openai.calls == []


def test_analyze_parses_llm_json(api_client, fake_openai):
    analysis = {"processes_personal_data": True, "risk_level": "Medium"}
    fake_openai.reply = json.dumps(analysis)
    _upload_txt(api_client, "Personal data is transferred outside the EEA.")

    response = api_client.post("/analyze", json={"question": "Summarize risks"})

    assert response.json() == {"analysis": analysis}
    assert "transferred outside the EEA" in fake_openai.calls[0]["messages"][1]["content"]


def test_analyze_reports_unparseable_llm_response(api_client, fake_openai):
    fake_openai.reply = "not json"
    _upload_txt(api_client, "Some clause.")

    response = api_client.post("/analyze", json={"question": "Summarize risks"})

    assert response.json() == {
        "analysis": {
            "error": "Failed to parse LLM response",
            "raw_response": "not json"
        }
    }
