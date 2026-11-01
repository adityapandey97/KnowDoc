import os
import tempfile
import pytest
from app.services.document_parser import document_parser
from app.core.exceptions import CorruptDocumentError, DocumentParsingError

def test_parse_empty_file_raises_corrupt_error():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        with pytest.raises(CorruptDocumentError):
            document_parser.parse_pdf(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_parse_nonexistent_file_raises_error():
    with pytest.raises(DocumentParsingError):
        document_parser.parse_pdf("nonexistent_file_12345.pdf")

def test_parse_minimal_valid_pdf_stream():
    # Valid minimal PDF structure
    minimal_pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 44>>stream\n"
        b"BT /F1 12 Tf 72 712 Td (Quarterly Revenue Report) Tj ET\n"
        b"endstream\n"
        b"endobj\n"
        b"xref\n"
        b"0 5\n"
        b"0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\n"
        b"startxref\n"
        b"190\n"
        b"%%EOF\n"
    )

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(minimal_pdf)
        tmp_path = tmp.name

    try:
        pages, is_scanned = document_parser.parse_pdf(tmp_path)
        assert len(pages) >= 1
        assert pages[0].page_number == 1
        assert "Quarterly Revenue Report" in pages[0].text
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

