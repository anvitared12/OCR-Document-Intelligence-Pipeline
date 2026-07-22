Smart Document Enity Resolution

Flowchart
Input
Upload a scanned document (ID card, invoice, application form, handwritten form, etc.)

↓
OCR
Extract text from the image

↓
Entity Extraction
Extract
Name, Email, Phone, Address

↓
Normalization
Convert text into a standard format

↓
Entity Matching
Compare against an existing database

↓
Confidence Score
Return the best matching person

↓
FastAPI Response
Return JSON


Technologies:
| Purpose          | Library      |
| ---------------- | ------------ |
| API              | FastAPI      |
| OCR              | EasyOCR      |
| Image Processing | OpenCV       |
| Matching         | RapidFuzz    |
| Database         | CSV + Pandas |
| Validation       | Pydantic     |

