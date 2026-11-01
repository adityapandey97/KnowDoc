from typing import List, Dict, Optional
from app.schemas.citations import Citation
from app.schemas.chat import SearchResult

class CitationService:
    """
    Validates and constructs verifiable source citations.
    Ensures every citation references a chunk that was genuinely retrieved.
    """

    def build_citations(self, search_results: List[SearchResult]) -> List[Citation]:
        citations: List[Citation] = []

        for idx, res in enumerate(search_results, start=1):
            # Extract high-relevance verbatim excerpt (up to 250 characters)
            content_clean = res.content.strip()
            excerpt = content_clean[:250] + ("..." if len(content_clean) > 250 else "")

            citations.append(
                Citation(
                    citation_id=f"cit_{idx}",
                    document_id=res.document_id,
                    document_name=res.document_name,
                    page_number=res.page_number,
                    chunk_id=res.chunk_id,
                    excerpt=excerpt,
                    similarity_score=res.similarity_score
                )
            )

        return citations

    def validate_citations_against_sources(
        self,
        citations: List[Citation],
        retrieved_results: List[SearchResult]
    ) -> List[Citation]:
        """
        Filters out any hallucinated or fabricated citations that do not match
        the document_id and page_number of actually retrieved chunks.
        """
        valid_map = {(r.document_id, r.page_number): r for r in retrieved_results}
        validated = []

        for c in citations:
            key = (c.document_id, c.page_number)
            if key in valid_map:
                validated.append(c)

        return validated

citation_service = CitationService()

