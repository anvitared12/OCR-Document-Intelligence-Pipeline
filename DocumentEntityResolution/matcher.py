import sys
import csv
import json
import re

from rapidfuzz import fuzz
from normalize import normalize_text

DEFAULT_DB_PATH = "database.csv"
MATCH_THRESHOLD = 50  

_DIGITS_RE = re.compile(r"\d+")


def load_database(csv_path: str = DEFAULT_DB_PATH) -> list:
    """Load database.csv into a list of dicts."""
    with open(csv_path, newline="") as f:
        return list(csv.DictReader(f))


def _digits_only(s: str) -> str:
    return "".join(_DIGITS_RE.findall(s or ""))


def _score_field(a, b, method, preprocess=normalize_text):
    if not a or not b:
        return None
    return method(preprocess(str(a)), preprocess(str(b)))


def score_record(extracted: dict, record: dict) -> dict:
    name_score = _score_field(extracted.get("name"), record.get("Name"), fuzz.ratio)
    address_score = _score_field(extracted.get("address"), record.get("Address"), fuzz.WRatio)
    phone_score = _score_field(
        extracted.get("phone"), record.get("Phone"), fuzz.ratio, preprocess=_digits_only
    )

    available = [s for s in (name_score, address_score, phone_score) if s is not None]
    confidence = sum(available) / len(available) if available else 0.0

    return {
        "name_score": name_score,
        "address_score": address_score,
        "phone_score": phone_score,
        "confidence": round(confidence, 2),
    }


def find_best_match(extracted: dict, database: list = None, csv_path: str = DEFAULT_DB_PATH) -> dict:
    if database is None:
        database = load_database(csv_path)

    best_record = None
    best_scores = None

    for record in database:
        scores = score_record(extracted, record)
        if best_scores is None or scores["confidence"] > best_scores["confidence"]:
            best_scores = scores
            best_record = record

    if best_record is None or best_scores["confidence"] < MATCH_THRESHOLD:
        return {"matched_person": None, "confidence": best_scores["confidence"] if best_scores else 0.0}

    return {
        "matched_person": best_record["Name"],
        "confidence": best_scores["confidence"],
    }


def main():
    if len(sys.argv) != 2:
        print('Usage: python match.py \'{"name": "...", "address": "...", "phone": "..."}\'')
        sys.exit(1)

    extracted = json.loads(sys.argv[1])
    result = find_best_match(extracted)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()