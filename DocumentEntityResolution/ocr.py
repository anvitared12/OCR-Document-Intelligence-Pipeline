"""
ocr.py

Job:
    Receive image (or PDF) -> Return text

Usage (as a module):
    from ocr import extract_text
    result = extract_text("path/to/image.png")
    result = extract_text("path/to/scanned.pdf")
    # {"text": "John Smith MG Road Bangalore 9876543210"}

Usage (CLI):
    python ocr.py path/to/image_or_pdf
"""

import sys
import json
import os
from pathlib import Path

from PIL import Image
import numpy as np
import cv2
import pytesseract
from pdf2image import convert_from_path

# --- Windows-specific setup -------------------------------------------------
# On Windows, pytesseract needs to be told where the tesseract.exe binary is
# (it's not auto-discovered unless it's on PATH). Set this via an environment
# variable so you don't have to hardcode/edit source paths on every machine:
#   setx TESSERACT_CMD "C:\Program Files\Tesseract-OCR\tesseract.exe"
# Same idea for Poppler (used by pdf2image for PDF -> image conversion):
#   setx POPPLER_PATH "C:\path\to\poppler-xx\Library\bin"
# On Linux/Mac these are usually already on PATH and can be left unset.
if os.environ.get("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]

POPPLER_PATH = os.environ.get("POPPLER_PATH")  # None is fine if on PATH
# -----------------------------------------------------------------------------

PDF_EXTENSIONS = {".pdf"}


def _preprocess(img: Image.Image) -> Image.Image:
    """
    Preprocess an image for OCR.

    Uses adaptive thresholding rather than a simple global threshold
    (e.g. Otsu) because real-world scans/photos of documents rarely
    have even lighting -- phone photos in particular have shadow
    gradients across the page. A global threshold blows out one side
    of the page or crushes the other; adaptive thresholding computes
    a local threshold per-region, so it copes with uneven lighting,
    shadows, and paper texture. This step is what lets Tesseract's
    layout analysis actually find text blocks on a "busy" photo of a
    page (as opposed to a clean flatbed scan).
    """
    arr = np.array(img.convert("L"))
    binarized = cv2.adaptiveThreshold(
        arr,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        35,  # block size: size of local neighborhood used per pixel
        15,  # C: constant subtracted from the local mean
    )
    return Image.fromarray(binarized)


def _ocr_image(img: Image.Image) -> str:
    """Run tesseract on a single preprocessed image, return raw text."""
    img = _preprocess(img)
    return pytesseract.image_to_string(img)


def extract_text(file_path: str) -> dict:
    """
    Receive an image OR a PDF (path to file), return extracted text.

    - If it's an image: OCR it directly.
    - If it's a PDF: convert each page to an image, OCR each page,
      and join the results in page order.

    Args:
        file_path: path to an image file (png, jpg, jpeg, tiff, bmp, etc.)
                    or a PDF file (.pdf)

    Returns:
        dict: {"text": "<extracted text, single line, whitespace-normalized>"}
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() in PDF_EXTENSIONS:
        pages = convert_from_path(str(path), dpi=300, poppler_path=POPPLER_PATH)
        raw_text = "\n".join(_ocr_image(page) for page in pages)
    else:
        img = Image.open(path)
        raw_text = _ocr_image(img)

    # Normalize: collapse all whitespace/newlines into single spaces,
    # matching the example output format.
    cleaned = " ".join(raw_text.split())

    return {"text": cleaned}


def main():
    if len(sys.argv) != 2:
        print("Usage: python ocr.py <image_path>")
        sys.exit(1)

    result = extract_text(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()