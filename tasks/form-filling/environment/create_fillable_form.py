from __future__ import annotations

from pathlib import Path
import sys


FIELDS = [
    ("full_name", "Full Name"),
    ("contact_email", "Contact Email"),
    ("phone_number", "Phone Number"),
    ("mailing_address", "Mailing Address"),
    ("date_of_birth", "Date of Birth"),
    ("nationality", "Nationality"),
    ("current_employer", "Current Employer"),
    ("target_position", "Target Position"),
    ("linkedin_profile", "LinkedIn Profile"),
    ("portfolio_url", "Portfolio URL"),
]


def escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_pdf_bytes() -> bytes:
    num_fields = len(FIELDS)
    field_start_id = 5
    content_id = field_start_id + num_fields
    font_id = content_id + 1
    annotation_refs = " ".join(f"{field_start_id + index} 0 R" for index in range(num_fields))

    objects: list[str] = [
        "<< /Type /Catalog /Pages 2 0 R /AcroForm 3 0 R >>",
        "<< /Type /Pages /Kids [4 0 R] /Count 1 >>",
        (
            f"<< /Fields [{annotation_refs}] /NeedAppearances true "
            f"/DA (/Helv 11 Tf 0 g) /DR << /Font << /Helv {font_id} 0 R >> >> >>"
        ),
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /Helv {font_id} 0 R >> >> "
            f"/Annots [{annotation_refs}] /Contents {content_id} 0 R >>"
        ),
    ]

    for index, (field_id, label) in enumerate(FIELDS):
        lower_y = 700 - (index * 55)
        upper_y = lower_y + 22
        rect = f"[320 {lower_y} 560 {upper_y}]"
        objects.append(
            (
                "<< /Type /Annot /Subtype /Widget /FT /Tx "
                f"/T ({escape_pdf_text(field_id)}) "
                f"/TU ({escape_pdf_text(label)}) "
                f"/F 4 /Rect {rect} /DA (/Helv 11 Tf 0 g) /P 4 0 R >>"
            )
        )

    content_lines = ["BT /Helv 16 Tf 1 0 0 1 50 760 Tm (Employment Application) Tj ET"]
    for index, (_, label) in enumerate(FIELDS):
        baseline_y = 707 - (index * 55)
        content_lines.append(
            f"BT /Helv 10 Tf 1 0 0 1 50 {baseline_y} Tm ({escape_pdf_text(label)}) Tj ET"
        )
    content_stream = "\n".join(content_lines).encode("ascii")
    objects.append(
        (
            f"<< /Length {len(content_stream)} >>\nstream\n"
            f"{content_stream.decode('ascii')}\nendstream"
        )
    )
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    pieces: list[bytes] = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = [0]
    current_offset = len(pieces[0])

    for object_id, object_body in enumerate(objects, start=1):
        offsets.append(current_offset)
        rendered = f"{object_id} 0 obj\n{object_body}\nendobj\n".encode("ascii")
        pieces.append(rendered)
        current_offset += len(rendered)

    xref_offset = current_offset
    xref_lines = [f"0 {len(objects) + 1}", "0000000000 65535 f "]
    xref_lines.extend(f"{offset:010d} 00000 n " for offset in offsets[1:])

    pieces.append(("xref\n" + "\n".join(xref_lines) + "\n").encode("ascii"))
    pieces.append(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    return b"".join(pieces)


def main() -> None:
    output_path = Path(sys.argv[1] if len(sys.argv) > 1 else "/app/fillable_form.pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(build_pdf_bytes())


if __name__ == "__main__":
    main()
