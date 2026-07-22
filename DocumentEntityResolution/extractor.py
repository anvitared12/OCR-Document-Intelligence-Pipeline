import sys
import json
import re

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

PHONE_RE = re.compile(r"(?:\+?91[\-\s]?|0)?([6-9]\d{9})\b")

MAX_NAME_TOKENS = 2 

def _extract_email(text: str):
    match = EMAIL_RE.search(text)
    return match.group(0) if match else None


def _extract_phone(text: str):
    """Returns (digits_only, full_matched_span) or (None, None)."""
    match = PHONE_RE.search(text)
    if not match:
        return None, None
    return match.group(1), match.group(0)


def _extract_name_and_address(remaining_text: str):
    
    tokens = remaining_text.split()

    name_tokens = []
    for token in tokens:
        if len(name_tokens) >= MAX_NAME_TOKENS:
            break
        if token.isalpha() and token.istitle():
            name_tokens.append(token)
        else:
            break

    name = " ".join(name_tokens) if name_tokens else None
    address_tokens = tokens[len(name_tokens):]
    address = " ".join(address_tokens) if address_tokens else None

    return name, address


def extract_entities(text: str) -> dict:
    flat = " ".join(text.split())

    email = _extract_email(flat)
    phone, phone_span = _extract_phone(flat)

    remaining = flat
    if email:
        remaining = remaining.replace(email, " ")
    if phone_span:
        remaining = remaining.replace(phone_span, " ")
    remaining = " ".join(remaining.split())

    name, address = _extract_name_and_address(remaining)

    return {
        "name": name,
        "phone": phone,
        "email": email,
        "address": address,
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python entity.py \"<text>\"")
        sys.exit(1)

    result = extract_entities(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()