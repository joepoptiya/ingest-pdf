"""Tests for PDF processor functionality."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ingest_pdf.exceptions import PDFProcessingError
from ingest_pdf.processor import PDFProcessor


class TestPDFProcessor:
    """Test cases for PDFProcessor."""

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_init_default(self):
        """Test processor initialization with default parameters."""
        with patch("ingest_pdf.processor.PDFExtractor") as mock_extractor:
            processor = PDFProcessor()
            assert processor.output_dir == Path(".")
            mock_extractor.assert_called_once()

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_init_custom(self, temp_dir):
        """Test processor initialization with custom parameters."""
        output_dir = temp_dir / "output"
        with patch("ingest_pdf.processor.PDFExtractor") as mock_extractor:
            processor = PDFProcessor(output_dir=output_dir)

            assert processor.output_dir == output_dir
            assert output_dir.exists()
            mock_extractor.assert_called_once()

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_file(self, sample_pdf):
        """Test processing a single PDF file."""
        mock_extractor = Mock()
        mock_extractor.extract_text.return_value = (
            "This is extracted text from the PDF document"
        )
        mock_extractor.extract_metadata.return_value = {
            "title": "Test Document",
            "page_count": 2,
            "file_size": 1234,
        }

        with patch("ingest_pdf.processor.PDFExtractor", return_value=mock_extractor):
            processor = PDFProcessor()
            result = processor.process_file(sample_pdf)

            assert result["file_name"] == sample_pdf.name
            assert result["file_path"] == str(sample_pdf)
            assert result["file_size"] > 0
            assert result["text_length"] > 0
            assert "extracted text from the PDF document" in result["extracted_text"]
            assert "metadata" in result
            assert "processed_at" in result

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_file_string_path(self, sample_pdf):
        """Test processing with string path."""
        mock_extractor = Mock()
        mock_extractor.extract_text.return_value = "Test content"
        mock_extractor.extract_metadata.return_value = {"title": "Test"}

        with patch("ingest_pdf.processor.PDFExtractor", return_value=mock_extractor):
            processor = PDFProcessor()
            result = processor.process_file(str(sample_pdf))

            assert result["file_name"] == sample_pdf.name

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_file_not_found(self, temp_dir):
        """Test processing non-existent file."""
        with patch("ingest_pdf.processor.PDFExtractor"):
            processor = PDFProcessor()
            non_existent_file = temp_dir / "does_not_exist.pdf"

            with pytest.raises(PDFProcessingError):
                processor.process_file(non_existent_file)

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_directory(self, pdf_directory):
        """Test processing directory with PDF files."""
        mock_extractor = Mock()
        mock_extractor.extract_text.return_value = "Test document number 1"
        mock_extractor.extract_metadata.return_value = {"title": "Test"}

        with patch("ingest_pdf.processor.PDFExtractor", return_value=mock_extractor):
            processor = PDFProcessor()
            results = processor.process_directory(pdf_directory)

            assert len(results) == 3
            for result in results:
                assert "file_name" in result
                assert "extracted_text" in result
                assert "document number" in result["extracted_text"]

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_directory_recursive(self, temp_dir):
        """Test recursive directory processing."""
        # Create nested directory structure
        sub_dir = temp_dir / "subdir"
        sub_dir.mkdir()

        # Create PDF in subdirectory
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_path = sub_dir / "nested.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Nested PDF document")
        c.save()

        mock_extractor = Mock()
        mock_extractor.extract_text.return_value = "Nested PDF document"
        mock_extractor.extract_metadata.return_value = {"title": "Nested"}

        with patch("ingest_pdf.processor.PDFExtractor", return_value=mock_extractor):
            processor = PDFProcessor()

            # Test non-recursive (should find 0 files)
            results_non_recursive = processor.process_directory(
                temp_dir, recursive=False
            )
            assert len(results_non_recursive) == 0

            # Test recursive (should find 1 file)
            results_recursive = processor.process_directory(temp_dir, recursive=True)
            assert len(results_recursive) == 1
            assert "nested.pdf" in results_recursive[0]["file_name"]

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_directory_empty(self, empty_directory):
        """Test processing empty directory."""
        with patch("ingest_pdf.processor.PDFExtractor"):
            processor = PDFProcessor()
            results = processor.process_directory(empty_directory)

            assert results == []

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_directory_not_found(self, temp_dir):
        """Test processing non-existent directory."""
        with patch("ingest_pdf.processor.PDFExtractor"):
            processor = PDFProcessor()
            non_existent_dir = temp_dir / "does_not_exist"

            with pytest.raises(PDFProcessingError):
                processor.process_directory(non_existent_dir)

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_save_results_single(self, temp_dir, sample_pdf):
        """Test saving single file results."""
        mock_extractor = Mock()
        mock_extractor.extract_text.return_value = "Test content"
        mock_extractor.extract_metadata.return_value = {"title": "Test"}

        with patch("ingest_pdf.processor.PDFExtractor", return_value=mock_extractor):
            processor = PDFProcessor(output_dir=temp_dir)
            result = processor.process_file(sample_pdf)

            output_file = processor.save_results(result, "test_results.json")

            assert output_file.exists()
            with open(output_file) as f:
                saved_data = json.load(f)
            assert saved_data == result

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_save_results_multiple(self, temp_dir, pdf_directory):
        """Test saving multiple file results."""
        mock_extractor = Mock()
        mock_extractor.extract_text.return_value = "Test content"
        mock_extractor.extract_metadata.return_value = {"title": "Test"}

        with patch("ingest_pdf.processor.PDFExtractor", return_value=mock_extractor):
            processor = PDFProcessor(output_dir=temp_dir)
            results = processor.process_directory(pdf_directory)

            output_file = processor.save_results(results, "batch_results.json")

            assert output_file.exists()
            with open(output_file) as f:
                saved_data = json.load(f)
            assert len(saved_data) == 3

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_save_results_auto_filename(self, temp_dir, sample_pdf):
        """Test saving with auto-generated filename."""
        mock_extractor = Mock()
        mock_extractor.extract_text.return_value = "Test content"
        mock_extractor.extract_metadata.return_value = {"title": "Test"}

        with patch("ingest_pdf.processor.PDFExtractor", return_value=mock_extractor):
            processor = PDFProcessor(output_dir=temp_dir)
            result = processor.process_file(sample_pdf)

            output_file = processor.save_results(result)

            assert output_file.exists()
            assert "pdf_processing_results_" in output_file.name
            assert output_file.name.endswith(".json")

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_extract_text_only(self, sample_pdf):
        """Test text-only extraction."""
        mock_extractor = Mock()
        mock_extractor.extract_text.return_value = (
            "This is the sample PDF document text"
        )

        with patch("ingest_pdf.processor.PDFExtractor", return_value=mock_extractor):
            processor = PDFProcessor()
            text = processor.extract_text_only(sample_pdf)

            assert isinstance(text, str)
            assert "sample PDF document" in text

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_get_file_info(self, sample_pdf):
        """Test getting file information."""
        mock_extractor = Mock()
        mock_extractor.extract_metadata.return_value = {
            "title": sample_pdf.stem,
            "author": None,
            "page_count": 1,
            "file_size": 1234,
        }

        with patch("ingest_pdf.processor.PDFExtractor", return_value=mock_extractor):
            processor = PDFProcessor()
            info = processor.get_file_info(sample_pdf)

            assert info["file_name"] == sample_pdf.name
            assert info["file_size"] > 0
            assert info["page_count"] == 1
            assert info["title"] == sample_pdf.stem

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_get_file_info_not_found(self, temp_dir):
        """Test getting info for non-existent file."""
        with patch("ingest_pdf.processor.PDFExtractor"):
            processor = PDFProcessor()
            non_existent_file = temp_dir / "does_not_exist.pdf"

            with pytest.raises(PDFProcessingError):
                processor.get_file_info(non_existent_file)
