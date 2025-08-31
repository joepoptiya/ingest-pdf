"""PDF processing and ingestion functionality."""

import json
import logging
from pathlib import Path
from typing import Any

from .exceptions import PDFProcessingError
from .extractor import PDFExtractor

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process and ingest PDF files."""

    def __init__(self, output_dir: Path | None = None) -> None:
        """Initialize the PDF processor.

        Args:
            output_dir: Directory to save processed results. If None, uses current directory.
        """
        self.output_dir = output_dir or Path(".")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.extractor = PDFExtractor()

    def process_file(self, pdf_path: str | Path) -> dict[str, Any]:
        """Process a single PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Dictionary containing processed results.

        Raises:
            PDFProcessingError: If processing fails.
        """
        pdf_path = Path(pdf_path)

        try:
            logger.info(f"Processing PDF: {pdf_path}")

            # Extract text and metadata
            text = self.extractor.extract_text(pdf_path)
            metadata = self.extractor.extract_metadata(pdf_path)

            # Prepare results
            results = {
                "file_path": str(pdf_path),
                "file_name": pdf_path.name,
                "file_size": pdf_path.stat().st_size,
                "text_length": len(text),
                "extracted_text": text,
                "metadata": metadata,
                "processed_at": self._get_timestamp(),
            }

            logger.info(f"Successfully processed {pdf_path}")
            return results

        except Exception as e:
            error_msg = f"Failed to process PDF {pdf_path}: {e}"
            logger.error(error_msg)
            raise PDFProcessingError(error_msg) from e

    def process_directory(
        self, directory_path: str | Path, recursive: bool = False
    ) -> list[dict[str, Any]]:
        """Process all PDF files in a directory.

        Args:
            directory_path: Path to the directory.
            recursive: Whether to search subdirectories recursively.

        Returns:
            List of processing results for each PDF file.

        Raises:
            PDFProcessingError: If directory processing fails.
        """
        directory_path = Path(directory_path)

        if not directory_path.is_dir():
            raise PDFProcessingError(f"Directory not found: {directory_path}")

        try:
            # Find PDF files
            pattern = "**/*.pdf" if recursive else "*.pdf"
            pdf_files = list(directory_path.glob(pattern))

            if not pdf_files:
                logger.warning(f"No PDF files found in {directory_path}")
                return []

            logger.info(f"Found {len(pdf_files)} PDF files to process")

            # Process each file
            results = []
            for pdf_file in pdf_files:
                try:
                    result = self.process_file(pdf_file)
                    results.append(result)
                except PDFProcessingError as e:
                    logger.error(f"Skipping {pdf_file}: {e}")
                    # Continue processing other files
                    continue

            logger.info(
                f"Successfully processed {len(results)} out of {len(pdf_files)} PDF files"
            )
            return results

        except Exception as e:
            error_msg = f"Failed to process directory {directory_path}: {e}"
            logger.error(error_msg)
            raise PDFProcessingError(error_msg) from e

    def save_results(
        self,
        results: dict[str, Any] | list[dict[str, Any]],
        output_file: str | None = None,
    ) -> Path:
        """Save processing results to a JSON file.

        Args:
            results: Processing results to save.
            output_file: Output filename. If None, generates a timestamp-based name.

        Returns:
            Path to the saved file.
        """
        if output_file is None:
            output_file = f"pdf_processing_results_{self._get_timestamp()}.json"

        output_path = self.output_dir / output_file

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"Results saved to {output_path}")
            return output_path

        except Exception as e:
            error_msg = f"Failed to save results to {output_path}: {e}"
            logger.error(error_msg)
            raise PDFProcessingError(error_msg) from e

    def extract_text_only(self, pdf_path: str | Path) -> str:
        """Extract only text from a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Extracted text.
        """
        return self.extractor.extract_text(Path(pdf_path))

    def get_file_info(self, pdf_path: str | Path) -> dict[str, str | int]:
        """Get basic information about a PDF file.

        Args:
            pdf_path: Path to the PDF file.

        Returns:
            Dictionary with basic file information.
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise PDFProcessingError(f"PDF file not found: {pdf_path}")

        metadata = self.extractor.extract_metadata(pdf_path)

        return {
            "file_path": str(pdf_path),
            "file_name": pdf_path.name,
            "file_size": pdf_path.stat().st_size,
            "page_count": metadata.get("page_count", 0),
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime

        return datetime.now().isoformat()
