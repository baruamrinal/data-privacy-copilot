from dotenv import load_dotenv

# Load .env before importing modules that read env vars at import time
load_dotenv()

from fastapi import FastAPI

from app.api.upload import router as upload_router
from app.api.query import router as query_router
from app.api.analyze import router as analyze_router

app = FastAPI()

app.include_router(upload_router)
app.include_router(query_router)
app.include_router(analyze_router)


@app.get("/")
def health():
    return {"status": "running"}