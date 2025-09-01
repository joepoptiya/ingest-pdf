"""PDF text extraction functionality."""

import logging
import os
from pathlib import Path
from typing import Any

import httpx
from llama_parse import LlamaParse  # type: ignore[import-untyped]
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from utils.context import RunContext

from .exceptions import PDFExtractionError, PDFNotFoundError, PDFReadError

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text and metadata from PDF files using LlamaParse."""

    def __init__(self, run_context: RunContext | None = None) -> None:
        """Initialize the PDF extractor with LlamaParse.

        Args:
            run_context: Run context containing run_id and other shared state.
            
        Environment Variables Required:
            LLAMA_CLOUD_API_KEY: API key for LlamaParse service

        Raises:
            PDFExtractionError: If API key is not configured
        """
        self.run_context = run_context or RunContext.create()

        api_key = os.getenv("LLAMA_CLOUD_API_KEY")
        if not api_key:
            raise PDFExtractionError(
                "LLAMA_CLOUD_API_KEY environment variable is required for LlamaParse"
            )

        self.parser = LlamaParse(
            api_key=api_key,
            result_type="markdown",  # Can be "markdown" or "text"
            language="en",
            verbose=self.run_context.verbose,
        )

    def extract_text(self, pdf_path: Path) -> str:
        """Extract text from a PDF file using LlamaParse.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Extracted text as a string.

        Raises:
            PDFNotFoundError: If the PDF file doesn't exist.
            PDFReadError: If the PDF file cannot be read.
            PDFExtractionError: If text extraction fails.
        """
        if not pdf_path.exists():
            raise PDFNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            return self._extract_with_llamaparse(pdf_path)
        except Exception as e:
            raise PDFExtractionError(
                f"Failed to extract text from {pdf_path}: {e}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
        reraise=True,
    )
    def _extract_with_llamaparse(self, pdf_path: Path) -> str:
        """Extract text using LlamaParse with retry logic.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Extracted text as a string.

        Raises:
            PDFReadError: If LlamaParse cannot process the PDF.
        """
        try:
            logger.info(f"Processing PDF with LlamaParse: {pdf_path} [run_id: {self.run_context.run_id}]")

            # Load and parse the document
            documents = self.parser.load_data(str(pdf_path))

            if not documents:
                logger.warning(f"No content extracted from PDF: {pdf_path}")
                return ""

            # Combine all document text
            text_parts = []
            for doc in documents:
                if doc.text:
                    text_parts.append(doc.text.strip())

            result = "\n\n".join(text_parts)
            logger.info(
                f"Successfully extracted {len(result)} characters from {pdf_path} [run_id: {self.run_context.run_id}]"
            )

            return result

        except Exception as e:
            logger.error(f"LlamaParse extraction failed for {pdf_path}: {e} [run_id: {self.run_context.run_id}]")
            raise PDFReadError(f"Cannot read PDF with LlamaParse: {e}") from e

    def extract_metadata(self, pdf_path: Path) -> dict[str, Any]:
        """Extract basic metadata from a PDF file.

        Note: LlamaParse focuses on text extraction. Basic metadata is derived
        from file system properties and text analysis.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Dictionary containing basic metadata.

        Raises:
            PDFNotFoundError: If the PDF file doesn't exist.
            PDFReadError: If the PDF file cannot be analyzed.
        """
        if not pdf_path.exists():
            raise PDFNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            stat = pdf_path.stat()

            # Extract text to analyze content
            text = self.extract_text(pdf_path)

            # Basic analysis
            lines = text.split("\n") if text else []
            non_empty_lines = [line.strip() for line in lines if line.strip()]

            # Estimate page count based on content structure
            # This is approximate since LlamaParse returns continuous text
            estimated_pages = max(1, len(text.split("\f")) if "\f" in text else 1)

            return {
                "title": pdf_path.stem,  # Use filename as title
                "author": None,  # LlamaParse doesn't extract PDF metadata
                "subject": None,
                "creator": None,
                "producer": "LlamaParse",
                "creation_date": stat.st_ctime,
                "modification_date": stat.st_mtime,
                "page_count": estimated_pages,
                "file_size": stat.st_size,
                "text_length": len(text),
                "line_count": len(non_empty_lines),
            }
        except PDFExtractionError:
            # Re-raise extraction errors
            raise
        except Exception as e:
            raise PDFReadError(f"Cannot analyze PDF metadata: {e}") from e

    def extract_page_text(self, pdf_path: Path, page_number: int) -> str:
        """Extract text from a specific page.

        Note: LlamaParse returns continuous text without page boundaries.
        This method provides approximate page-based text extraction.

        Args:
            pdf_path: Path to the PDF file.
            page_number: Page number (0-indexed).

        Returns:
            Text from the specified page (approximate).

        Raises:
            PDFNotFoundError: If the PDF file doesn't exist.
            PDFReadError: If the PDF file cannot be read.
            PDFExtractionError: If the page number is invalid.
        """
        if not pdf_path.exists():
            raise PDFNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            # Get full text first
            full_text = self.extract_text(pdf_path)

            # Try to split by form feed characters (page breaks)
            pages = full_text.split("\f") if "\f" in full_text else [full_text]

            if page_number >= len(pages):
                # If no page breaks detected, estimate based on text length
                if len(pages) == 1 and full_text:
                    # Estimate pages based on text length (rough approximation)
                    avg_chars_per_page = 2000  # Approximate characters per page
                    total_chars = len(full_text)
                    estimated_pages = max(1, total_chars // avg_chars_per_page)

                    if page_number >= estimated_pages:
                        raise PDFExtractionError(
                            f"Page {page_number} not found in PDF (estimated {estimated_pages} pages)"
                        )

                    # Return a chunk of text approximating the requested page
                    start_pos = page_number * avg_chars_per_page
                    end_pos = min((page_number + 1) * avg_chars_per_page, total_chars)
                    return full_text[start_pos:end_pos]
                else:
                    raise PDFExtractionError(
                        f"Page {page_number} not found in PDF (found {len(pages)} pages)"
                    )

            return pages[page_number].strip()

        except PDFExtractionError:
            raise
        except Exception as e:
            raise PDFReadError(f"Cannot read page {page_number} from PDF: {e}") from e
