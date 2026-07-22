"""
app.py

FastAPI server exposing the OCR + entity-matching pipeline over HTTP.

Endpoints:
    GET  /              -> health check
    POST /ocr            -> upload image/PDF, get raw OCR text
    POST /match-document -> upload image/PDF, run full pipeline:
                             OCR -> Extraction -> Normalization ->
                             Matching -> return matched person + confidence

Run:
    uvicorn app:app --reload

Test:
    curl -X POST "http://127.0.0.1:8000/match-document" \
         -F "file=@document.jpg"
"""

import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException

from ocr import extract_text
from extractor import extract_entities
from normalizer import normalize_text
from matcher import find_best_match, load_database, DEFAULT_DB_PATH

app = FastAPI(title="Document Matching Service")

# Load the database once at startup rather than on every request.
_database = load_database(DEFAULT_DB_PATH)

ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".pdf"}


def _save_upload_to_tmp(file: UploadFile) -> str:
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Allowed: {sorted(ALLOWED_SUFFIXES)}",
        )
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        return tmp.name


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    """
    Receive an uploaded image or PDF, return extracted text.
    """
    tmp_path = _save_upload_to_tmp(file)
    try:
        result = extract_text(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return result


@app.post("/match-document")
async def match_document_endpoint(file: UploadFile = File(...), debug: bool = False):
    """
    Full pipeline: Upload -> OCR -> Extraction -> Normalization -> Matching.

    Args:
        file:  uploaded image or PDF of a document
        debug: if true, include intermediate pipeline outputs
               (raw OCR text, extracted entities, normalized entities,
               per-field similarity scores) alongside the final result

    Returns:
        {"matched_person": <name or null>, "confidence": <0-100>}
        (plus a "details" key with intermediate outputs if debug=true)
    """
    tmp_path = _save_upload_to_tmp(file)

    try:
        # 1. OCR
        ocr_result = extract_text(tmp_path)
        raw_text = ocr_result["text"]

        # 2. Extraction
        entities = extract_entities(raw_text)

        # 3. Normalization (name + address; phone/email left as-is --
        #    lowercasing/punctuation-stripping isn't meaningful for
        #    digits, and would break email addresses)
        normalized_entities = dict(entities)
        for field in ("name", "address"):
            if entities.get(field):
                normalized_entities[field] = normalize_text(entities[field])

        # 4. Matching (match.py normalizes internally too, so passing
        #    either the raw or normalized entities here is equivalent;
        #    we pass normalized for clarity of intent)
        match_result = find_best_match(normalized_entities, database=_database)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    if not debug:
        return match_result

    return {
        **match_result,
        "details": {
            "ocr_text": raw_text,
            "extracted_entities": entities,
            "normalized_entities": normalized_entities,
        },
    }