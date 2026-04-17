#!/bin/bash
set -euo pipefail

python3 - <<'PY'
from pathlib import Path

SCRIPT = r'''#!/usr/bin/env python3
import json
import re
import shutil
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PDF_PATH = Path("/app/fillable_form.pdf")
DOCUMENT_DIR = Path("/app/documents")
OUTPUT_JSON = Path("/app/field_mapping.json")
OUTPUT_PDF = Path("/app/filled_form.pdf")
DOCUMENT_ORDER = [
    "sample_application",
    "sample_personal_info",
    "sample_resume",
]

FIELD_PROFILES = {
    "full_name": {
        "types": ["full_name"],
        "query": "full name applicant name identity personal information",
    },
    "contact_email": {
        "types": ["contact_email"],
        "query": "contact email email address applicant contact",
    },
    "phone_number": {
        "types": ["phone_number"],
        "query": "phone number primary phone contact number",
    },
    "mailing_address": {
        "types": ["mailing_address"],
        "query": "mailing address current address residence contact address",
    },
    "date_of_birth": {
        "types": ["date_of_birth"],
        "query": "date of birth dob birthday applicant identity",
    },
    "nationality": {
        "types": ["nationality"],
        "query": "nationality citizenship personal identity",
    },
    "current_employer": {
        "types": ["current_employer"],
        "query": "current employer company organization work experience",
    },
    "target_position": {
        "types": ["target_position"],
        "query": "target position job title role applied for employment",
    },
    "linkedin_profile": {
        "types": [],
        "query": "linkedin profile social profile",
    },
    "portfolio_url": {
        "types": [],
        "query": "portfolio url website personal site",
    },
}

PATTERNS = {
    "full_name": [
        r"Full Name:\s*([^\n]+)",
        r"^Name:\s*([^\n]+)",
        r"^#\s*([^\n]+)",
    ],
    "contact_email": [
        r"Email(?: Address)?:\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})",
    ],
    "phone_number": [
        r"Phone(?: Number)?(?: \([^)]+\))?:\s*(\(\d{3}\)\s*\d{3}-\d{4})",
    ],
    "mailing_address": [
        r"(?:Current Address|Address):\s*([^\n]+)",
    ],
    "date_of_birth": [
        r"Date of Birth:\s*([^\n]+)",
    ],
    "nationality": [
        r"Nationality:\s*([^\n]+)",
    ],
    "current_employer": [
        r"Current Employer:\s*([^\n]+)",
    ],
    "target_position": [
        r"Job Title:\s*([^\n]+)",
        r"Position:\s*([^\n]+)",
        r"^###\s*([^\n]+)",
    ],
}


def normalize_value(value: str) -> str:
    compact = " ".join(value.replace("**", "").split())
    return compact.rstrip(",;")


def load_documents() -> tuple[dict[str, str], int]:
    documents = {}
    total_chars_processed = 0

    for name in DOCUMENT_ORDER:
        path = DOCUMENT_DIR / f"{name}.txt"
        text = path.read_text(encoding="utf-8")
        documents[name] = text
        total_chars_processed += len(text)

    return documents, total_chars_processed


def extract_candidates(documents: dict[str, str]) -> list[dict[str, str]]:
    candidates = []
    seen = set()

    for source in DOCUMENT_ORDER:
        text = documents[source]
        for field_type, patterns in PATTERNS.items():
            for pattern in patterns:
                for match in re.findall(pattern, text, flags=re.MULTILINE):
                    value = normalize_value(match)
                    key = (field_type, value, source)
                    if not value or key in seen:
                        continue
                    seen.add(key)
                    candidates.append(
                        {
                            "field_type": field_type,
                            "value": value,
                            "source": source,
                            "search_text": (
                                f"{field_type.replace('_', ' ')} "
                                f"{value} {source.replace('_', ' ')}"
                            ),
                        }
                    )
    return candidates


def read_pdf_fields() -> list[dict[str, str]]:
    reader = PdfReader(str(PDF_PATH))
    raw_fields = reader.get_fields() or {}
    fields = []
    for field_id, field_info in raw_fields.items():
        label = field_info.get("/TU") or field_info.get("/T") or field_id
        fields.append({"id": field_id, "label": str(label)})
    return fields


def choose_candidate(
    field_id: str,
    field_label: str,
    candidates: list[dict[str, str]],
) -> dict[str, str] | None:
    profile = FIELD_PROFILES.get(field_id, {"types": [], "query": field_label})
    allowed_types = set(profile["types"])
    scoped_candidates = [
        candidate for candidate in candidates if candidate["field_type"] in allowed_types
    ]
    if not scoped_candidates:
        return None

    query_text = f"{field_id.replace('_', ' ')} {field_label} {profile['query']}"
    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([query_text] + [c["search_text"] for c in scoped_candidates])
    scores = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
    best_index = int(scores.argmax())
    best_candidate = dict(scoped_candidates[best_index])
    best_candidate["score"] = float(scores[best_index])
    return best_candidate


def build_report(
    fields: list[dict[str, str]],
    candidates: list[dict[str, str]],
    total_chars_processed: int,
) -> dict[str, object]:
    mapped_fields = {}
    unmapped_fields = []
    field_match_confidence = {}

    for field in fields:
        match = choose_candidate(field["id"], field["label"], candidates)
        if match is None:
            unmapped_fields.append(field["id"])
            continue

        mapped_fields[field["id"]] = {
            "field_name": field["label"],
            "value": match["value"],
            "source": match["source"],
        }
        field_match_confidence[field["id"]] = round(match["score"], 4)

    return {
        "pdf_file": PDF_PATH.name,
        "mapped_fields": mapped_fields,
        "unmapped_fields": unmapped_fields,
        "total_mapped": len(mapped_fields),
        "total_unmapped": len(unmapped_fields),
        "rag_stats": {
            "documents_processed": len(DOCUMENT_ORDER),
            "total_chars_processed": total_chars_processed,
            "retrieval_method": "TF-IDF cosine similarity over extracted candidates",
            "candidate_matches_evaluated": len(candidates),
            "field_match_confidence": field_match_confidence,
        },
    }


def write_report(report: dict[str, object]) -> None:
    OUTPUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def write_filled_pdf(mapped_fields: dict[str, dict[str, str]]) -> None:
    values = {field_id: payload["value"] for field_id, payload in mapped_fields.items()}
    try:
        writer = PdfWriter(clone_from=str(PDF_PATH))
        for page in writer.pages:
            writer.update_page_form_field_values(page, values, auto_regenerate=False)
        with open(OUTPUT_PDF, "wb") as handle:
            writer.write(handle)
    except Exception:
        shutil.copyfile(PDF_PATH, OUTPUT_PDF)


def main() -> None:
    documents, total_chars_processed = load_documents()
    candidates = extract_candidates(documents)
    fields = read_pdf_fields()
    report = build_report(fields, candidates, total_chars_processed)
    write_report(report)
    write_filled_pdf(report["mapped_fields"])


if __name__ == "__main__":
    main()
'''

Path("/app/form_filler.py").write_text(SCRIPT, encoding="utf-8")
PY

python3 /app/form_filler.py
