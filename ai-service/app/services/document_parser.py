import os
import re
import zlib
from typing import List, Tuple
from app.schemas.documents import ExtractedPage
from app.core.exceptions import DocumentParsingError, CorruptDocumentError
from app.core.logging import logger

class DocumentParser:
    """
    Parses PDF binaries, extracting text page-by-page while preserving
    physical page indexes and flagging potentially scanned documents.
    Supports PyMuPDF (fitz), pypdf, and native fallback stream decompression.
    """

    def parse_pdf(self, file_path: str) -> Tuple[List[ExtractedPage], bool]:
        """
        Parses PDF file. Returns tuple of (pages, is_scanned).
        """
        if not os.path.exists(file_path):
            raise DocumentParsingError(f"PDF file does not exist at path: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise CorruptDocumentError("PDF file is completely empty (0 bytes).")

        # 1. Try PyMuPDF (fitz)
        try:
            import fitz
            return self._parse_with_fitz(file_path)
        except ImportError:
            pass
        except Exception as e:
            logger.warn(f"PyMuPDF failed to parse {file_path}: {str(e)}; trying pypdf")

        # 2. Try pypdf
        try:
            import pypdf
            return self._parse_with_pypdf(file_path)
        except ImportError:
            pass
        except Exception as e:
            logger.warn(f"pypdf failed to parse {file_path}: {str(e)}; falling back to native parser")

        # 3. Native Python PDF Stream Parser
        return self._parse_native(file_path)

    def _parse_with_fitz(self, file_path: str) -> Tuple[List[ExtractedPage], bool]:
        import fitz
        doc = fitz.open(file_path)
        pages: List[ExtractedPage] = []
        total_chars = 0

        for idx, page in enumerate(doc, start=1):
            text = page.get_text() or ""
            cleaned = text.strip()
            char_count = len(cleaned)
            total_chars += char_count
            pages.append(
                ExtractedPage(
                    page_number=idx,
                    text=cleaned,
                    char_count=char_count,
                    is_empty_or_scanned=char_count < 20
                )
            )

        is_scanned = (len(pages) > 0 and total_chars < 50)
        return pages, is_scanned

    def _parse_with_pypdf(self, file_path: str) -> Tuple[List[ExtractedPage], bool]:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        pages: List[ExtractedPage] = []
        total_chars = 0

        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            cleaned = text.strip()
            char_count = len(cleaned)
            total_chars += char_count
            pages.append(
                ExtractedPage(
                    page_number=idx,
                    text=cleaned,
                    char_count=char_count,
                    is_empty_or_scanned=char_count < 20
                )
            )

        is_scanned = (len(pages) > 0 and total_chars < 50)
        return pages, is_scanned

    def _parse_native(self, file_path: str) -> Tuple[List[ExtractedPage], bool]:
        """
        Pure Python fallback for environments without fitz/pypdf.
        Decompresses Flate streams and extracts textual operands.
        """
        try:
            with open(file_path, "rb") as f:
                content = f.read()
        except Exception as e:
            raise CorruptDocumentError(f"Could not read PDF file: {str(e)}")

        if not content.startswith(b"%PDF-"):
            raise CorruptDocumentError("File does not start with valid PDF magic bytes '%PDF-'.")

        pages: List[ExtractedPage] = []
        # Find stream blocks
        stream_matches = re.findall(b"stream\r?\n(.*?)endstream", content, re.DOTALL)
        extracted_texts = []

        for raw_stream in stream_matches:
            decompressed = None
            try:
                decompressed = zlib.decompress(raw_stream)
            except Exception:
                # Try raw or with header stripped
                try:
                    decompressed = zlib.decompress(raw_stream, -zlib.MAX_WBITS)
                except Exception:
                    decompressed = raw_stream

            if decompressed:
                # Extract text in parentheses (text) Tj or [(text)] TJ
                text_matches = re.findall(rb"\((.*?)\)\s*Tj", decompressed)
                if text_matches:
                    page_text = " ".join([t.decode("latin1", errors="ignore") for t in text_matches])
                    extracted_texts.append(page_text.strip())

        if not extracted_texts:
            # Fallback regex over whole file for text strings
            text_matches = re.findall(rb"\(([\w\s.,;:!?-]{4,})\)", content)
            if text_matches:
                fallback_str = " ".join([t.decode("latin1", errors="ignore") for t in text_matches])
                extracted_texts.append(fallback_str)

        if not extracted_texts:
            # Return single empty page marked as scanned
            return [ExtractedPage(page_number=1, text="", char_count=0, is_empty_or_scanned=True)], True

        total_chars = 0
        for idx, text in enumerate(extracted_texts, start=1):
            cleaned = text.strip()
            char_count = len(cleaned)
            total_chars += char_count
            pages.append(
                ExtractedPage(
                    page_number=idx,
                    text=cleaned,
                    char_count=char_count,
                    is_empty_or_scanned=char_count < 20
                )
            )

        is_scanned = (total_chars < 50)
        return pages, is_scanned

document_parser = DocumentParser()

