Build a local, offline RAG-style tool that reads a fillable PDF form and maps information from the supplied text documents into the form fields.

Resources already available in the container:

- `/app/fillable_form.pdf`
- `/app/documents/sample_application.txt`
- `/app/documents/sample_personal_info.txt`
- `/app/documents/sample_resume.txt`

Create `/app/form_filler.py` and run it so that it produces:

- `/app/field_mapping.json`
- `/app/filled_form.pdf`

Requirements for `form_filler.py`:

1. Inspect `/app/fillable_form.pdf` with `pypdf` and discover the fillable field IDs from the PDF itself.
2. Read the three supplied text documents and extract candidate values with regular expressions.
3. Use `sklearn.feature_extraction.text.TfidfVectorizer` together with `sklearn.metrics.pairwise.cosine_similarity` to decide which extracted value best matches each PDF field.
4. Only map fields that have explicit evidence in the supplied documents. Do not invent values. Leave unsupported fields in `unmapped_fields`.
5. Save the JSON report to `/app/field_mapping.json`.
6. Save a filled PDF copy to `/app/filled_form.pdf`.

Expected mapping coverage for this specific form:

- The supplied documents contain enough explicit evidence to map these field IDs:
  - `full_name`
  - `contact_email`
  - `phone_number`
  - `mailing_address`
  - `date_of_birth`
  - `nationality`
  - `current_employer`
  - `target_position`
- The only field IDs that should remain in `unmapped_fields` are:
  - `linkedin_profile`
  - `portfolio_url`

The JSON report must use this exact top-level structure:

```json
{
  "pdf_file": "fillable_form.pdf",
  "mapped_fields": {
    "field_id": {
      "field_name": "Human readable field name from the PDF",
      "value": "Extracted value",
      "source": "sample_application | sample_personal_info | sample_resume"
    }
  },
  "unmapped_fields": ["field_id"],
  "total_mapped": 0,
  "total_unmapped": 0,
  "rag_stats": {
    "documents_processed": 3,
    "total_chars_processed": 0,
    "retrieval_method": "string"
  }
}
```

Additional constraints:

- Work completely offline. Do not download anything.
- Use the preinstalled Python environment and libraries in the image.
- The script must be runnable with `python3 /app/form_filler.py`.
- The three valid `source` values are `sample_application`, `sample_personal_info`, and `sample_resume`.
- In `rag_stats.retrieval_method`, include the literal substring `TF-IDF`.
