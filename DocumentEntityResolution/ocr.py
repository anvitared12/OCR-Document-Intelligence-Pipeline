import sys
import json
import os
from pathlib import Path
 
from PIL import Image
import numpy as np
import cv2
import pytesseract
from pdf2image import convert_from_path


if os.environ.get("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]
 
POPPLER_PATH = os.environ.get("POPPLER_PATH")  # None is fine if on PATH

PDF_EXTENSIONS = {".pdf"}

def _preprocess(img: Image.Image) -> Image.Image:
    arr = np.array(img.convert("L"))
    binarized = cv2.adaptiveThreshold(arr,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,35,15)
    return Image.fromarray(binarized)

def _ocr_image(img:Image.Image)-> str:
    img = _preprocess(img)
    return pytesseract.image_to_string(img)

def extract_text(file_path:str) -> dict:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix.lower()in PDF_EXTENSIONS:
        pages=convert_from_path(str(path),dpi=300)
        raw_text="\n".join(_ocr_image(page) for page in pages)
    else:
        img=Image.open(path)
        raw_text = _ocr_image(img)

        cleaned = " ".join(raw_text.split())
        return {"text":cleaned}

    def main():
        if len(sys.argv) !=2:
            print("Usage: python ocr.py <image_path>")
            sys.exit(1) 
            result = extract_text(sys.argv[1])
            print(json.dumps(result, indent=2))

    if __name__ == "__main__":
        main() 
