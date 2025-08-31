"""PDF text extraction functionality."""

import logging
from pathlib import Path

import pdfplumber
from PyPDF2 import PdfReader

from .exceptions import PDFExtractionError, PDFNotFoundError, PDFReadError

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text and metadata from PDF files."""

    def __init__(self, use_pdfplumber: bool = True) -> None:
        """Initialize the PDF extractor.

        Args:
            use_pdfplumber: Whether to use pdfplumber for extraction (default: True).
                           If False, uses PyPDF2.
        """
        self.use_pdfplumber = use_pdfplumber

    def extract_text(self, pdf_path: Path) -> str:
        """Extract text from a PDF file.

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
            if self.use_pdfplumber:
                return self._extract_with_pdfplumber(pdf_path)
            else:
                return self._extract_with_pypdf2(pdf_path)
        except Exception as e:
            raise PDFExtractionError(
                f"Failed to extract text from {pdf_path}: {e}"
            ) from e

    def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extract text using pdfplumber."""
        text_parts = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            raise PDFReadError(f"Cannot read PDF with pdfplumber: {e}") from e

        return "\n\n".join(text_parts)

    def _extract_with_pypdf2(self, pdf_path: Path) -> str:
        """Extract text using PyPDF2."""
        text_parts = []

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            raise PDFReadError(f"Cannot read PDF with PyPDF2: {e}") from e

        return "\n\n".join(text_parts)

    def extract_metadata(self, pdf_path: Path) -> dict[str, str | None]:
        """Extract metadata from a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Dictionary containing PDF metadata.

        Raises:
            PDFNotFoundError: If the PDF file doesn't exist.
            PDFReadError: If the PDF file cannot be read.
        """
        if not pdf_path.exists():
            raise PDFNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PdfReader(file)
                metadata = pdf_reader.metadata

                return {
                    "title": metadata.get("/Title"),
                    "author": metadata.get("/Author"),
                    "subject": metadata.get("/Subject"),
                    "creator": metadata.get("/Creator"),
                    "producer": metadata.get("/Producer"),
                    "creation_date": (
                        str(metadata.get("/CreationDate"))
                        if metadata.get("/CreationDate")
                        else None
                    ),
                    "modification_date": (
                        str(metadata.get("/ModDate"))
                        if metadata.get("/ModDate")
                        else None
                    ),
                    "page_count": len(pdf_reader.pages),
                }
        except Exception as e:
            raise PDFReadError(f"Cannot read PDF metadata: {e}") from e

    def extract_page_text(self, pdf_path: Path, page_number: int) -> str:
        """Extract text from a specific page.

        Args:
            pdf_path: Path to the PDF file.
            page_number: Page number (0-indexed).

        Returns:
            Text from the specified page.

        Raises:
            PDFNotFoundError: If the PDF file doesn't exist.
            PDFReadError: If the PDF file cannot be read.
            PDFExtractionError: If the page number is invalid.
        """
        if not pdf_path.exists():
            raise PDFNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            if self.use_pdfplumber:
                with pdfplumber.open(pdf_path) as pdf:
                    if page_number >= len(pdf.pages):
                        raise PDFExtractionError(f"Page {page_number} not found in PDF")
                    page = pdf.pages[page_number]
                    return page.extract_text() or ""
            else:
                with open(pdf_path, "rb") as file:
                    pdf_reader = PdfReader(file)
                    if page_number >= len(pdf_reader.pages):
                        raise PDFExtractionError(f"Page {page_number} not found in PDF")
                    page = pdf_reader.pages[page_number]
                    return page.extract_text() or ""
        except PDFExtractionError:
            raise
        except Exception as e:
            raise PDFReadError(f"Cannot read page {page_number} from PDF: {e}") from e
