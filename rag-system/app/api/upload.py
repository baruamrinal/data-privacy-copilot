# app/api/upload.py

from fastapi import APIRouter, UploadFile, File
import os
import shutil
from uuid import uuid4

from app.parser.document_parser import parse_document
from app.chunking.text_chunker import chunk_text
from app.embeddings.embedding_service import generate_embeddings
from app.vector_store.qdrant_store import store_embeddings

router = APIRouter()

UPLOAD_DIR = "data/uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):

    file_id = str(uuid4())

    file_path = f"{UPLOAD_DIR}/{file_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    parsed_data = parse_document(file_path)

    chunks = chunk_text(parsed_data["text"])

    embeddings = generate_embeddings(chunks)

    response = store_embeddings(
        chunks=chunks,
        embeddings=embeddings,
        metadata={
            "document_id": file_id,
            "filename": file.filename
        }
    )

    return {
        "message": "Document indexed in Qdrant successfully",
        "document_id": file_id,
        "filename": file.filename,
        "total_chunks": len(chunks),
        "vectors_stored": response["vectors_stored"]
    }