# Data Privacy Copilot

An AI assistant for reviewing privacy and data-processing agreements (DPAs). Upload a contract, then ask compliance questions in plain English ("Does this agreement allow cross-border transfer of personal data?") or get a structured risk summary. Answers are grounded only in clauses retrieved from the uploaded document.

## How it works

```
Upload:  PDF / DOCX / TXT → parse → chunk → embed (bge-large-en-v1.5) → store in Qdrant
Query:   question → query expansion → vector search (top 10) → rerank (bge-reranker-large) → top 3 clauses → GPT-4.1 answer
Analyze: question → vector search (top 15) → GPT-4.1 → structured JSON compliance report
```

| Component | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Parsing | PyMuPDF (PDF, with repeated page headers/footers removed), python-docx (DOCX) |
| Chunking | LangChain `RecursiveCharacterTextSplitter` (900 chars, 150 overlap) |
| Embeddings | `BAAI/bge-large-en-v1.5` (sentence-transformers) |
| Reranking | `BAAI/bge-reranker-large` cross-encoder |
| Vector store | Qdrant (collection `privacy_compliance_docs`) |
| LLM | OpenAI GPT-4.1 |

## Project structure

```
data-privacy-copilot/
├── input-files/                 # Sample DPA (fictional Quillfeather-Online-DPA.pdf)
└── rag-system/
    ├── app/
    │   ├── main.py              # FastAPI app entry point
    │   ├── api/                 # /upload-document, /query, /analyze
    │   ├── parser/              # PDF / DOCX / TXT text extraction
    │   ├── chunking/            # Text splitting
    │   ├── embeddings/          # Embedding model
    │   ├── vector_store/        # Qdrant (active) and FAISS stores
    │   └── llm/                 # OpenAI client and prompts
    ├── data/uploads/            # Uploaded files
    ├── requirements.txt
    └── .env.example
```

## Prerequisites

- Python 3.12
- Docker (for Qdrant)
- An OpenAI API key

## Setup

```bash
cd rag-system
```

Create and activate a virtual environment:

| OS | Commands |
|---|---|
| macOS / Linux | `python3 -m venv venv` then `source venv/bin/activate` |
| Windows PowerShell | `python -m venv venv` then `venv\Scripts\Activate.ps1` |
| Windows CMD | `python -m venv venv` then `venv\Scripts\activate.bat` |

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your API key by copying the example file and editing it:

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

```
OPENAI_API_KEY=your-openai-api-key
```

`.env` is git-ignored. Never commit real keys.

## Running

1. Start Qdrant (in a separate terminal):

   ```bash
   docker run -p 6333:6333 -v ./qdrant_storage:/qdrant/storage qdrant/qdrant
   ```

2. Start the API from `rag-system/`:

   ```bash
   python -m uvicorn app.main:app --reload
   ```

   The first start downloads the embedding and reranker models, which takes a few minutes.

3. Open http://127.0.0.1:8000/docs for the interactive API docs.

## API

| Method | Endpoint | Body | Description |
|---|---|---|---|
| GET | `/` | none | Health check |
| POST | `/upload-document` | multipart `file` | Parse, chunk, embed and index a document |
| POST | `/query` | `{"question": "..."}` | Answer a question with cited clauses |
| POST | `/analyze` | `{"question": "..."}` | Return a structured JSON compliance report |

### Examples

macOS / Linux:

```bash
curl -X POST http://127.0.0.1:8000/upload-document \
  -F "file=@../input-files/Quillfeather-Online-DPA.pdf"

curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Does this agreement allow cross-border transfer of personal data?"}'
```

Windows PowerShell:

```powershell
curl.exe -X POST http://127.0.0.1:8000/upload-document `
  -F "file=@..\input-files\Quillfeather-Online-DPA.pdf"

Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/query `
  -ContentType "application/json" `
  -Body (@{ question = "Does this agreement allow cross-border transfer of personal data?" } | ConvertTo-Json)
```

### `/analyze` response shape

```json
{
  "analysis": {
    "processes_personal_data": true,
    "personal_data_categories": [],
    "cross_border_transfer": true,
    "retention_clause_present": true,
    "security_obligations_present": true,
    "subprocessors_allowed": true,
    "gdpr_applicable": true,
    "risk_level": "Low | Medium | High",
    "summary": ""
  }
}
```

## Troubleshooting

- **Connection refused on upload/query**: Qdrant isn't running on `localhost:6333`.
- **OpenAI authentication error**: check `OPENAI_API_KEY` in `rag-system/.env`.
- **`JSON decode error` from curl on Windows**: PowerShell 7.3+ passes `\"` literally. Use `Invoke-RestMethod` as shown above, or single-quoted JSON without backslashes.
- **`Activate.ps1` is blocked**: run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once.

## License

[MIT](LICENSE)
