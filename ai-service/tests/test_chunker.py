import pytest
from app.schemas.documents import ExtractedPage
from app.services.chunking_service import ChunkingService

def test_chunking_service_splits_and_preserves_page_numbers():
    chunker = ChunkingService(chunk_size=50, chunk_overlap=10)

    page1 = ExtractedPage(
        page_number=1,
        text="Section 1: Operating profits grew by 15% year over year across European markets. " * 3,
        char_count=200
    )
    page2 = ExtractedPage(
        page_number=2,
        text="Section 2: Capital expenditure allocations for green energy infrastructure initiatives. " * 3,
        char_count=240
    )

    chunks = chunker.chunk_pages(
        pages=[page1, page2],
        document_id="doc_xyz",
        user_id="user_123",
        document_name="annual_report.pdf"
    )

    assert len(chunks) >= 2
    # Verify page numbers are preserved
    page_numbers = {c.page_number for c in chunks}
    assert 1 in page_numbers
    assert 2 in page_numbers

    # Verify chunk metadata
    for c in chunks:
        assert c.document_id == "doc_xyz"
        assert c.user_id == "user_123"
        assert c.document_name == "annual_report.pdf"
        assert c.token_estimate > 0
        assert len(c.content) >= 30

def test_chunking_service_ignores_empty_pages():
    chunker = ChunkingService()
    empty_page = ExtractedPage(page_number=1, text="   ", char_count=3, is_empty_or_scanned=True)
    chunks = chunker.chunk_pages(pages=[empty_page], document_id="doc_empty", user_id="user_1")
    assert len(chunks) == 0
