# 📄 Smart Document Entity Resolution System

An OCR-powered Document Intelligence pipeline that extracts structured information from scanned documents, normalizes noisy text, performs fuzzy entity matching against a reference database, and returns confidence-scored matches through REST APIs.

This project demonstrates how modern AI systems process messy real-world documents containing inconsistent names, addresses, OCR errors, and incomplete information.

---

## 🚀 Features

- 📄 Upload scanned documents or images
- 🔍 OCR-based text extraction using EasyOCR
- 📝 Automatic extraction of:
  - Name
  - Address
  - Phone Number
  - Email
- 🧹 Text normalization to handle inconsistent formatting
- 🤝 Entity Resolution using fuzzy string matching
- 📊 Confidence score for each matched record
- ⚡ FastAPI REST APIs
- 📂 CSV-based reference database
- 📈 Modular architecture for easy extension

---

# 🏗️ System Architecture

```
               Upload Document
                      │
                      ▼
               Image Preprocessing
                 (OpenCV)
                      │
                      ▼
               OCR Extraction
                 (EasyOCR)
                      │
                      ▼
             Raw Extracted Text
                      │
                      ▼
            Entity Extraction Module
        (Regex + Rule-based Processing)
                      │
                      ▼
           Text Normalization Module
                      │
                      ▼
          Entity Resolution Engine
             (RapidFuzz Matching)
                      │
                      ▼
           Confidence Score Engine
                      │
                      ▼
             FastAPI JSON Response
```

---

# 📁 Project Structure

```
Smart-Document-Entity-Resolution/
│
├── app.py
├── ocr.py
├── extractor.py
├── matcher.py
├── normalizer.py
├── database.csv
├── requirements.txt
├── README.md
│
├── sample_documents/
│   ├── sample1.png
│   ├── sample2.jpg
│   └── sample3.pdf
│
└── static/
```

---

# 🛠️ Tech Stack

## Languages

- Python

## Backend

- FastAPI
- Uvicorn

## OCR

- EasyOCR

## Image Processing

- OpenCV

## Entity Matching

- RapidFuzz

## Data Processing

- Pandas

## Validation

- Pydantic

---
Installation of tesseract
https://github.com/UB-Mannheim/tesseract/wiki

Installation of poppler
https://github.com/oschwartz10612/poppler-windows/releases

# ▶️ Run the Application

```bash
uvicorn app:app --reload
```

Open

```
http://127.0.0.1:8000/docs
```

to access the interactive Swagger UI.

---

# 📥 API Endpoint

## POST

```
/match-document
```

### Input

Upload

- Image (.jpg, .png)
- PDF

---

### Sample Request

```
Document

↓

sample_form.jpg
```

---
