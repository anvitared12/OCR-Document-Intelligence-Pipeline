import sys
import json
import re
import string

ABBREVIATIONS = {
    "rd": "road",
    "st": "street",
    "ave": "avenue",
    "blvd": "boulevard",
    "ln": "lane",
    "dr": "drive",
    "hwy": "highway",
    "apt": "apartment",
    "flr": "floor",
    "bldg": "building",
    "opp": "opposite",
    "nr": "near",
    "no": "number",
    "cor": "corner",
    "sq": "square",
    "bengaluru": "bangalore",
    "mumbai": "mumbai",   
    "calcutta": "kolkata",
    "madras": "chennai",
    "poona": "pune",
    "baroda": "vadodara",
    "cochin": "kochi",
    "gurgaon": "gurugram",
}

_PUNCT_RE = re.compile(f"[{re.escape(string.punctuation)}]")
_WHITESPACE_RE = re.compile(r"\s+")


def _remove_punctuation(text: str) -> str:
    return _PUNCT_RE.sub(" ", text)


def _collapse_whitespace(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip()


def _expand_abbreviations(text: str) -> str:
    tokens = text.split()
    expanded = [ABBREVIATIONS.get(tok, tok) for tok in tokens]
    return " ".join(expanded)


def normalize_text(text: str) -> str:
    text = text.lower()
    text = _remove_punctuation(text)
    text = _collapse_whitespace(text)
    text = _expand_abbreviations(text)
    text = _collapse_whitespace(text)
    return text


def main():
    if len(sys.argv) != 2:
        print("Usage: python normalize.py \"<text>\"")
        sys.exit(1)

    result = {"normalized": normalize_text(sys.argv[1])}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()