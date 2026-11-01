from app.domain.models import ExtractedPage
from app.rag.chunking.chunker import RecursiveChunker

def test_recursive_chunker_splits_text():
    chunker = RecursiveChunker(chunk_size=50, chunk_overlap=10) # Small chunk size for testing

    sample_text = (
        "This is paragraph one of the financial report.\n\n"
        "This is paragraph two containing detailed operational metrics and EBITDA margins.\n\n"
        "This is paragraph three summarizing future capital expenditure allocations."
    )

    page = ExtractedPage(page_number=1, text=sample_text, char_count=len(sample_text))
    chunks = chunker.chunk_pages([page], document_id="doc_123", user_id="user_abc")

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk.document_id == "doc_123"
        assert chunk.user_id == "user_abc"
        assert chunk.page_number == 1
        assert len(chunk.content) > 0

