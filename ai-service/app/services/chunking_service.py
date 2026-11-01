from typing import List, Optional
from app.schemas.documents import ExtractedPage, DocumentChunk
from app.core.config import settings

class ChunkingService:
    """
    Recursively splits pages into bounded text chunks respecting natural boundaries
    (paragraphs, lines, sentences) while strictly preserving physical page metadata.
    """

    def __init__(
        self,
        chunk_size: int = settings.default_chunk_size,
        chunk_overlap: int = settings.default_chunk_overlap
    ):
        # 1 token ~= 4 characters approximation
        self.chunk_size_chars = chunk_size * 4
        self.chunk_overlap_chars = chunk_overlap * 4
        self.separators = ["\n\n", "\n", ". ", " "]

    def chunk_pages(
        self,
        pages: List[ExtractedPage],
        document_id: str,
        user_id: str,
        document_name: Optional[str] = None
    ) -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        global_chunk_idx = 0

        for page in pages:
            text = page.text
            if not text or len(text.strip()) < settings.min_chunk_length:
                continue

            page_chunks = self._split_text(text)
            for chunk_content in page_chunks:
                clean_content = chunk_content.strip()
                if len(clean_content) < settings.min_chunk_length:
                    continue

                chunks.append(
                    DocumentChunk(
                        chunk_index=global_chunk_idx,
                        document_id=document_id,
                        document_name=document_name,
                        user_id=user_id,
                        page_number=page.page_number,
                        content=clean_content,
                        token_estimate=len(clean_content) // 4,
                        metadata={
                            "page": page.page_number,
                            "char_length": len(clean_content)
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

chunking_service = ChunkingService()

