from typing import List
from app.domain.models import ExtractedPage, TextChunk

class RecursiveChunker:
    """
    Splits document pages into semantic chunks respecting boundaries
    (paragraphs, lines, sentences) while preserving exact page number citations.
    """

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        # Character approximations: 1 token ~= 4 characters
        self.chunk_size_chars = chunk_size * 4
        self.chunk_overlap_chars = chunk_overlap * 4
        self.separators = ["\n\n", "\n", ". ", " "]

    def chunk_pages(
        self,
        pages: List[ExtractedPage],
        document_id: str,
        user_id: str
    ) -> List[TextChunk]:
        chunks: List[TextChunk] = []
        global_chunk_idx = 0

        for page in pages:
            text = page.text
            if not text:
                continue

            page_chunks = self._split_text(text)
            for chunk_content in page_chunks:
                chunks.append(
                    TextChunk(
                        chunk_index=global_chunk_idx,
                        document_id=document_id,
                        user_id=user_id,
                        page_number=page.page_number,
                        content=chunk_content,
                        token_estimate=len(chunk_content) // 4,
                        metadata={
                            "page": page.page_number,
                            "char_length": len(chunk_content)
                        }
                    )
                )
                global_chunk_idx += 1

        return chunks

    def _split_text(self, text: str) -> List[str]:
        if len(text) <= self.chunk_size_chars:
            return [text]

        results = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + self.chunk_size_chars, text_len)
            
            # If not at end of text, seek nearest separator to avoid cutting words
            if end < text_len:
                best_sep_idx = -1
                for sep in self.separators:
                    idx = text.rfind(sep, start + self.chunk_overlap_chars, end)
                    if idx != -1:
                        best_sep_idx = idx + len(sep)
                        break
                if best_sep_idx != -1:
                    end = best_sep_idx

            chunk_slice = text[start:end].strip()
            if chunk_slice:
                results.append(chunk_slice)

            if end >= text_len:
                break

            start = max(end - self.chunk_overlap_chars, start + 1)

        return results

chunker = RecursiveChunker()

