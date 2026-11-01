import os
from typing import List
from pypdf import PdfReader
from app.domain.models import ExtractedPage
from app.core.logging import logger
from app.core.errors import DocumentParsingError

class PDFParser:
    """
    Parses PDF binaries, extracting text page-by-page while preserving
    physical page indexes and flagging potentially scanned documents.
    """

    def parse(self, file_path: str) -> List[ExtractedPage]:
        if not os.path.exists(file_path):
            raise DocumentParsingError(f"PDF file does not exist at path: {file_path}")

        try:
            reader = PdfReader(file_path)
            total_pages = len(reader.pages)
            pages: List[ExtractedPage] = []
            total_chars = 0

            for idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                cleaned_text = page_text.strip()
                char_count = len(cleaned_text)
                total_chars += char_count

                is_empty = char_count < 10

                pages.append(
                    ExtractedPage(
                        page_number=idx,
                        text=cleaned_text,
                        char_count=char_count,
                        is_empty_or_scanned=is_empty
                    )
                )

            # Detect if document appears to be scanned (< 50 text characters across entire PDF)
            if total_pages > 0 and total_chars < 50:
                logger.warn(f"Document at {file_path} yielded only {total_chars} characters; likely scanned.")

            return pages
        except Exception as e:
            logger.error(f"Error parsing PDF file: {str(e)}")
            raise DocumentParsingError(f"Failed to extract text from PDF: {str(e)}")

pdf_parser = PDFParser()

