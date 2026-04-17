import json
from pathlib import Path

from pypdf import PdfReader


EXPECTED_MAPPINGS = {
    "full_name": {
        "values": {"Alex Johnson"},
        "sources": {"sample_application", "sample_personal_info", "sample_resume"},
    },
    "contact_email": {
        "values": {"alex.johnson@example.com"},
        "sources": {"sample_application", "sample_personal_info", "sample_resume"},
    },
    "phone_number": {
        "values": {"(555) 123-4567"},
        "sources": {"sample_application", "sample_personal_info", "sample_resume"},
    },
    "mailing_address": {
        "values": {"123 Tech Lane, San Francisco, CA 94105"},
        "sources": {"sample_application", "sample_personal_info", "sample_resume"},
    },
    "date_of_birth": {
        "values": {"05/12/1991", "May 12, 1991"},
        "sources": {"sample_application", "sample_personal_info"},
    },
    "nationality": {
        "values": {"American"},
        "sources": {"sample_application", "sample_personal_info"},
    },
    "current_employer": {
        "values": {"TechCorp Inc."},
        "sources": {"sample_personal_info"},
    },
    "target_position": {
        "values": {"Senior Software Engineer"},
        "sources": {"sample_application", "sample_personal_info", "sample_resume"},
    },
}
EXPECTED_UNMAPPED = {"linkedin_profile", "portfolio_url"}


def load_report() -> dict:
    report_path = Path("/app/field_mapping.json")
    assert report_path.exists(), f"{report_path} does not exist"
    with open(report_path, encoding="utf-8") as report_file:
        return json.load(report_file)


def load_pdf_fields() -> set[str]:
    fields = PdfReader("/app/fillable_form.pdf").get_fields()
    assert fields, "fillable_form.pdf should expose fillable fields"
    return set(fields.keys())


def test_outputs_exist():
    assert Path("/app/form_filler.py").exists(), "/app/form_filler.py should exist"
    assert Path("/app/field_mapping.json").exists(), "/app/field_mapping.json should exist"
    assert Path("/app/filled_form.pdf").exists(), "/app/filled_form.pdf should exist"
    assert Path("/app/filled_form.pdf").stat().st_size > 0, "filled_form.pdf should not be empty"


def test_pdf_fixture_is_fillable():
    field_ids = load_pdf_fields()
    expected_ids = set(EXPECTED_MAPPINGS) | EXPECTED_UNMAPPED
    assert field_ids == expected_ids, "The task PDF should contain the expected field IDs"


def test_report_structure():
    report = load_report()

    assert report["pdf_file"] == "fillable_form.pdf"
    assert isinstance(report["mapped_fields"], dict)
    assert isinstance(report["unmapped_fields"], list)
    assert isinstance(report["total_mapped"], int)
    assert isinstance(report["total_unmapped"], int)
    assert isinstance(report["rag_stats"], dict)

    rag_stats = report["rag_stats"]
    assert rag_stats["documents_processed"] == 3
    assert rag_stats["total_chars_processed"] > 300
    assert isinstance(rag_stats["retrieval_method"], str)
    assert "tf-idf" in rag_stats["retrieval_method"].lower()


def test_expected_mappings_and_unmapped_fields():
    report = load_report()
    field_ids = load_pdf_fields()
    mapped_fields = report["mapped_fields"]

    assert set(mapped_fields.keys()) == set(EXPECTED_MAPPINGS), "Unexpected mapped field set"
    assert set(report["unmapped_fields"]) == EXPECTED_UNMAPPED, "Unexpected unmapped field set"
    assert report["total_mapped"] == len(EXPECTED_MAPPINGS)
    assert report["total_unmapped"] == len(EXPECTED_UNMAPPED)
    assert report["total_mapped"] + report["total_unmapped"] == len(field_ids)

    for field_id, expectation in EXPECTED_MAPPINGS.items():
        payload = mapped_fields[field_id]
        assert payload["field_name"], f"{field_id} should include a field_name"
        assert payload["value"] in expectation["values"], f"Unexpected value for {field_id}"
        assert payload["source"] in expectation["sources"], f"Unexpected source for {field_id}"


def test_script_uses_pdf_regex_and_tfidf():
    script = Path("/app/form_filler.py").read_text(encoding="utf-8")

    assert "PdfReader" in script, "Script should inspect the PDF with pypdf"
    assert "import re" in script, "Script should use regular expressions"
    assert "TfidfVectorizer" in script, "Script should use TF-IDF"
    assert "cosine_similarity" in script, "Script should use cosine similarity"


def test_filled_pdf_is_readable():
    reader = PdfReader("/app/filled_form.pdf")
    assert len(reader.pages) >= 1, "filled_form.pdf should be a readable PDF"
