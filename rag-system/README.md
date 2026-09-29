macOS / Linux:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Windows (PowerShell):
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt

Windows (Command Prompt):
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt

If PowerShell blocks the activate script, run this once:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

Run the bellow command after updating requirements.tx for any additional package
pip install -r requirements.txt


Now start the server:
uvicorn app.main:app --reload


Upload curl:
curl -X POST "http://127.0.0.1:8000/upload-document" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/Users/mrinal/projects/data-privacy-copilot/input-files/Amplitude-Online-DPA.pdf"

Response:
{"message":"File uploaded successfully","document_id":"df0aed6e-230c-4f55-8f7a-5d9b3545bf1a","filename":"Amplitude-Online-DPA.pdf","path":"data/uploads/df0aed6e-230c-4f55-8f7a-5d9b3545bf1a_Amplitude-Online-DPA.pdf"}%


pip install torch



Windows
Create and activate venv (see setup at the top):
python -m venv venv
venv\Scripts\Activate.ps1


python -m uvicorn app.main:app --reload

Upload document:
curl.exe -X POST "http://127.0.0.1:8000/upload-document" `
  -H "accept: application/json" `
  -F "file=@C:\Users\lovin\OneDrive\projects\data-privacy-copilot\input-files\Amplitude-Online-DPA.pdf"

Query:
curl.exe -X POST "http://127.0.0.1:8000/query" `
  -H "Content-Type: application/json" `
  -d '{\"question\":\"Does this agreement allow cross-border transfer of personal data?\"}'

  pip install qdrant-client


Persistent Embedding Storage:
docker run -p 6333:6333 qdrant/qdrant

Then integrate Python client:
pip install qdrant-client

API KEY:
Copy .env.example to .env and set your key (.env is git-ignored, never commit it):
macOS / Linux:  cp .env.example .env
Windows:        copy .env.example .env

OPENAI_API_KEY=your-openai-api-key