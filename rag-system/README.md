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

**macOS / Linux**

```bash
curl -X POST "http://127.0.0.1:8000/upload-document" \
  -H "accept: application/json" \
  -F "file=@../input-files/Amplitude-Online-DPA.pdf"
```

**Windows (PowerShell)**

```powershell
curl.exe -X POST "http://127.0.0.1:8000/upload-document" `
  -H "accept: application/json" `
  -F "file=@..\input-files\Amplitude-Online-DPA.pdf"
```

Response (example values):

```json
{
  "message": "Document indexed in Qdrant successfully",
  "document_id": "df0aed6e-230c-4f55-8f7a-5d9b3545bf1a",
  "filename": "Amplitude-Online-DPA.pdf",
  "total_chunks": 120,
  "vectors_stored": 120
}
```

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
