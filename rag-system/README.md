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
  "document_id": "ffa89079-6903-4f91-b0ea-b61d83071bac",
  "filename": "Quillfeather-Online-DPA.pdf",
  "total_chunks": 22,
  "vectors_stored": 22
}
```

PDFs are split into chunks of about 900 characters with 150 characters of overlap. Page headers and footers that repeat on at least half the pages are removed before chunking, so they don't appear in matches.

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
  "answer": "Yes, this agreement allows cross-border transfer of personal data.\n\nClause 2 (11.2) states that for transfers of personal data originating from the European Economic Area (EEA) to countries without an adequacy decision, the parties agree to incorporate the Standard Contractual Clauses (SCCs) into the Data Processing Agreement (DPA). Clause 1 (11.3) further addresses transfers from the United Kingdom and Switzerland, specifying the application of the UK Addendum and the SCCs, respectively. Additionally, Clause 2 (11.1) notes that personal data may be hosted in the United States or the European Union, and subprocessors may access personal data from locations listed in Schedule C.\n\nTherefore, the agreement explicitly provides mechanisms (such as SCCs and the UK Addendum) to permit cross-border transfers of personal data.",
  "total_matches": 3,
  "matches": [
    {
      "vector_score": 0.701,
      "rerank_score": 0.946,
      "document": "Quillfeather-Online-DPA.pdf",
      "text": "applies; in Clause 9 Option 2 (general written authorization) applies with the notice period set out in Section\n5.3; in Clause 11 the optional language does not apply; in Clauses 17 and 18 the governing law and courts\nare those of Ireland. Annexes I and II of the SCCs are completed by Schedules A and B.\n11.3 UK and Swiss Transfers. For transfers from the United Kingdom, the UK Addendum applies, with\nTable 4 selecting that neither party may terminate the UK Addendum. For transfers from Switzerland, the\nSCCs apply with references to the GDPR read as references to the Swiss Federal Act on Data Protection,\nand the competent supervisory authority is the Swiss Federal Data Protection and Information Commissioner.\n11.4 Data Privacy Framework. Quillfeather self-certifies to the EU-U.S. Data Privacy Framework, the UK"
    },
    {
      "vector_score": 0.708,
      "rerank_score": 0.054,
      "document": "Quillfeather-Online-DPA.pdf",
      "text": "11. International Data Transfers\n11.1 Hosting Location. Personal Data is hosted in the data center region selected by Customer: the United\nStates (default) or the European Union (Frankfurt, Germany). Subprocessors may access Personal Data\nfrom the locations listed in Schedule C.\n11.2 EEA Transfers. To the extent Personal Data originating from the European Economic Area is\ntransferred to a country that has not received an adequacy decision, the parties agree that Module Two\n(Controller to Processor) and, where applicable, Module Three (Processor to Processor) of the SCCs are\nincorporated into this DPA by reference, with the following selections: in Clause 7 the optional docking clause\napplies; in Clause 9 Option 2 (general written authorization) applies with the notice period set out in Section"
    },
    {
      "vector_score": 0.644,
      "rerank_score": 0.028,
      "document": "Quillfeather-Online-DPA.pdf",
      "text": "Nature and purpose of Processing: Collection, storage, analysis, and visualization of product usage data\nto provide Customer with product analytics, reporting, experimentation, and customer support.\nRetention: As described in Section 9 of the DPA.\nTransfers to Subprocessors: As described in Schedule C, for the duration of the Agreement.\nC. Competent Supervisory Authority\nThe supervisory authority of the EU Member State in which Customer is established or, where Customer is\nnot established in the EU, the Irish Data Protection Commission.\nSchedule B - Technical and Organizational Security Measures (Annex II to the SCCs)\nEncryption. Personal Data is encrypted in transit using TLS 1.2 or higher and at rest using AES-256.\nEncryption keys are managed in a dedicated key management service and rotated at least annually."
    }
  ]
}
```

- `answer`: GPT-4.1 response based only on the top 3 reranked clauses. "Clause 1, 2, 3" is the order of the retrieved chunks; the numbers in brackets, such as "(11.2)", are the agreement's own section numbers.
- `expanded_query`: the question plus synonyms, when it contains keywords such as `pii`, `gdpr`, `cross-border` or `retention`.
- `vector_score`: cosine similarity from Qdrant, used to shortlist 10 candidates. For this embedding model, about 0.75+ is a strong match and 0.65–0.75 is related.
- `rerank_score`: cross-encoder relevance from 0 to 1. Above 0.7 means the chunk answers the question; below 0.3 is weak evidence. Results are sorted by this score, and all top 3 are sent to GPT-4.1 regardless of score.
- `text`: the matched chunk, truncated to 1,200 characters.

## 6. Run the tests

```bash
pip install -r requirements-dev.txt
python -m pytest
```

For a coverage report, listing the lines each file's tests don't reach:

```bash
python -m pytest --cov=app --cov-report=term-missing
```

The tests run offline. They replace the embedding and reranker models with lightweight fakes, use an in-memory Qdrant instead of `localhost:6333`, and stub the OpenAI client, so you don't need Docker or an API key.

### Pull request auto-approval

Every PR to `main` runs [`.github/workflows/pr-auto-approve.yml`](../.github/workflows/pr-auto-approve.yml). The bot approves the PR only if:

- all tests pass, and
- coverage of `app/` is at least 90%.

Otherwise it requests changes, with a link to the failing run. Each new push re-runs the check. To check locally before pushing:

```bash
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=90
```
