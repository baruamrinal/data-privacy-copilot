# RAG System

FastAPI service for the Data Privacy Copilot. See the [project README](../README.md) for an overview.

All commands below are run from the `rag-system/` directory.

## 1. Set up the virtual environment

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Windows (Command Prompt)**

```bat
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

If PowerShell blocks the activate script, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

After adding a package to `requirements.txt`, re-run:

```bash
pip install -r requirements.txt
```

## 2. Configure the API key

Copy `.env.example` to `.env` and set your key. `.env` is git-ignored; never commit it.

```bash
cp .env.example .env        # macOS / Linux
copy .env.example .env      # Windows
```

```
OPENAI_API_KEY=your-openai-api-key
```

## 3. Start Qdrant

Qdrant provides persistent embedding storage on `localhost:6333`. Run it in a separate terminal:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

## 4. Start the server

```bash
python -m uvicorn app.main:app --reload
```

Interactive API docs: http://127.0.0.1:8000/docs

## 5. Call the API

### Upload a document

The examples use [`Quillfeather-Online-DPA.pdf`](../input-files/Quillfeather-Online-DPA.pdf), a fictional agreement included for testing.

**macOS / Linux**

```bash
curl -X POST "http://127.0.0.1:8000/upload-document" \
  -H "accept: application/json" \
  -F "file=@../input-files/Quillfeather-Online-DPA.pdf"
```

**Windows (PowerShell)**

```powershell
curl.exe -X POST "http://127.0.0.1:8000/upload-document" `
  -H "accept: application/json" `
  -F "file=@..\input-files\Quillfeather-Online-DPA.pdf"
```

**Postman export (bash / Git Bash)**

```bash
curl --location 'http://127.0.0.1:8000/upload-document' \
--header 'accept: application/json' \
--form 'file=@"../input-files/Quillfeather-Online-DPA.pdf"'
```

Don't set a `Content-Type` header manually for uploads. `--form` sets it, including the multipart boundary.

Response (`document_id` is a new UUID on every upload):

```json
{
  "message": "Document indexed in Qdrant successfully",
  "document_id": "250d6d71-1f50-4975-920b-405faae5e672",
  "filename": "Quillfeather-Online-DPA.pdf",
  "total_chunks": 74,
  "vectors_stored": 74
}
```

Upload each document only once. Re-uploading indexes it again and creates duplicate matches.

### Ask a question

**macOS / Linux**

```bash
curl -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "Does this agreement allow cross-border transfer of personal data?"}'
```

**Windows (PowerShell)**

```powershell
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/query" `
  -ContentType "application/json" `
  -Body (@{ question = "Does this agreement allow cross-border transfer of personal data?" } | ConvertTo-Json)
```

Response, with only the Quillfeather DPA uploaded (the `answer` wording varies between runs):

```json
{
  "question": "Does this agreement allow cross-border transfer of personal data?",
  "expanded_query": "does this agreement allow cross-border transfer of personal data? international transfer data transfer transfer outside EEA standard contractual clauses SCC",
  "answer": "Yes, the agreement allows cross-border transfer of personal data.\n\nClause 1 states that if personal data is transferred to a country that has not received an adequacy decision, the parties agree to use the Standard Contractual Clauses (SCCs), specifically Module Two (Controller to Processor) and, where applicable, Module Three (Processor to Processor). This indicates that cross-border transfers are permitted, provided appropriate safeguards (such as SCCs) are in place.\n\nClause 2 and Clause 3 further reference the possibility of subprocessors accessing personal data from different locations and specify hosting locations, supporting the interpretation that cross-border transfers are contemplated.\n\nReferences: Clause 1, Clause 2, Clause 3.",
  "total_matches": 3,
  "matches": [
    {
      "vector_score": 0.636,
      "rerank_score": 0.223,
      "document": "Quillfeather-Online-DPA.pdf",
      "text": "transferred to a country that has not received an adequacy decision, the parties agree that Module Two\n(Controller to Processor) and, where applicable, Module Three (Processor to Processor) of the SCCs are"
    },
    {
      "vector_score": 0.676,
      "rerank_score": 0.174,
      "document": "Quillfeather-Online-DPA.pdf",
      "text": "States (default) or the European Union (Frankfurt, Germany). Subprocessors may access Personal Data\nfrom the locations listed in Schedule C.\n11.2 EEA Transfers. To the extent Personal Data originating from the European Economic Area is"
    },
    {
      "vector_score": 0.642,
      "rerank_score": 0.13,
      "document": "Quillfeather-Online-DPA.pdf",
      "text": "100 Example Avenue, Suite 400, Springfield, EX 00000\nPage 3 of 6  |  FICTIONAL SAMPLE - NOT A REAL AGREEMENT\nfollowing a Personal Data Breach.\n11. International Data Transfers\n11.1 Hosting Location. Personal Data is hosted in the data center region selected by Customer: the United"
    }
  ]
}
```

- `answer`: GPT-4.1 response based only on the top 3 reranked clauses. "Clause 1, 2, 3" refer to the order of the retrieved chunks, not the agreement's section numbers.
- `expanded_query`: the question plus synonyms, when it contains keywords such as `pii`, `gdpr`, `cross-border` or `retention`.
- `vector_score`: cosine similarity from Qdrant. `rerank_score`: cross-encoder relevance (higher is better). Results are sorted by `rerank_score`.
- `text`: the matched chunk, truncated to 1,200 characters.
