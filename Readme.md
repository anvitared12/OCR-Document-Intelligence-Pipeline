# OCR Document Intelligence Pipeline

Upload a scanned document (image or PDF) and get back the matching person record from a database, with a confidence score — using OCR, entity extraction, text normalization, and fuzzy string matching. No ML models required.

## Pipeline

```
Upload → OCR → Entity Extraction → Normalization → Fuzzy Matching → JSON result
```

| Stage | File | Job |
|---|---|---|
| OCR | `ocr.py` | Image/PDF → raw text (Tesseract, with adaptive thresholding for photographed/uneven-lit documents) |
| Extraction | `extractor.py` | Raw text → `{name, address, phone, email}` via regex + heuristics |
| Normalization | `normalizer.py` | Lowercase, strip punctuation, collapse whitespace, expand abbreviations (`Rd`→`Road`, `Bengaluru`→`Bangalore`, etc.) |
| Matching | `matcher.py` | Compare extracted entities against `database.csv` using RapidFuzz; returns best match + confidence |
| API | `app.py` | FastAPI server tying it all together |

## Setup

```bash
pip install -r requirements.txt
```

Also required (not installable via pip):
- **Tesseract OCR** — [Windows installer](https://github.com/UB-Mannheim/tesseract/wiki)
- **Poppler** — [Windows build](https://github.com/oschwartz10612/poppler-windows/releases) (needed for PDF support)

Set these environment variables (Windows example):
```powershell
setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
setx POPPLER_PATH "C:\path\to\poppler\Library\bin"
```
(Restart your terminal after running `setx`.)

## Run

```bash
python -m uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive Swagger docs.

## API

**POST** `/match-document`

Upload a document image/PDF. Returns:
```json
{
  "matched_person": "John Smith",
  "confidence": 95.4
}
```

Add `?debug=true` to also see the raw OCR text and extracted/normalized entities.

## Notes

- Confidence is the average of name, address, and phone similarity scores (0–100). Email is extracted but not scored.
- A confidence below ~50% returns `matched_person: null` (no match found) instead of a false positive.
- `database.csv` contains ~50 sample records for testing.
