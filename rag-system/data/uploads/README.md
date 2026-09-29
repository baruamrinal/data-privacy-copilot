# Uploads

Documents uploaded through `POST /upload-document` are saved here as `<document_id>_<original_filename>` before being parsed, chunked and indexed in Qdrant.

Contents of this folder are git-ignored, since uploads may contain confidential contracts or personal data. Only this README and `.gitkeep` are tracked, to keep the folder in the repo.

Deleting files here does not remove their embeddings from Qdrant.
