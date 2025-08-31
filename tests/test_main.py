"""Tests for CLI functionality."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch

from click.testing import CliRunner

from ingest_pdf.main import cli


class TestCLI:
    """Test cases for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "PDF ingestion and processing tool" in result.output

    def test_cli_version(self):
        """Test CLI version command."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_command(self, sample_pdf):
        """Test process command."""
        mock_extractor = Mock()
        mock_extractor.extract_text.return_value = "Sample PDF document text"
        mock_extractor.extract_metadata.return_value = {
            "title": "Test",
            "page_count": 1,
        }

        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_file.return_value = {
                "file_name": sample_pdf.name,
                "extracted_text": "Sample PDF document text",
                "metadata": {"title": "Test"},
                "file_size": 1234,
                "text_length": 25,
            }
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(cli, ["process", str(sample_pdf)])
            assert result.exit_code == 0

            # Parse JSON output
            output_data = json.loads(result.output)
            assert "file_name" in output_data
            assert "extracted_text" in output_data
            assert sample_pdf.name == output_data["file_name"]

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_command_text_only(self, sample_pdf):
        """Test process command with text-only flag."""
        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.extract_text_only.return_value = (
                "Sample PDF document text extracted"
            )
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(
                cli, ["process", str(sample_pdf), "--text-only"]
            )
            assert result.exit_code == 0
            assert "Sample PDF document text" in result.output

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_process_command_save_results(self, sample_pdf, temp_dir):
        """Test process command with save results flag."""
        with self.runner.isolated_filesystem():
            # Copy the sample PDF to the isolated filesystem
            import shutil

            isolated_pdf = Path("sample.pdf")
            shutil.copy2(sample_pdf, isolated_pdf)

            with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
                mock_processor = Mock()
                mock_processor.process_file.return_value = {
                    "file_name": "sample.pdf",
                    "text": "content",
                }
                mock_processor.save_results.return_value = Path("./results.json")
                # Create a dummy file to simulate save_results
                Path("./results.json").touch()
                mock_processor_class.return_value = mock_processor

                result = self.runner.invoke(
                    cli,
                    ["process", "sample.pdf", "--save-results", "--output-dir", "."],
                )
                assert result.exit_code == 0
                assert "Results saved to" in result.output


    def test_process_command_not_found(self):
        """Test process command with non-existent file."""
        result = self.runner.invoke(cli, ["process", "nonexistent.pdf"])
        assert result.exit_code == 2  # Click returns 2 for file not found errors
        assert "Error" in result.output

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_batch_command(self, pdf_directory):
        """Test batch processing command."""
        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_directory.return_value = [
                {"file_name": "doc1.pdf", "text": "content1"},
                {"file_name": "doc2.pdf", "text": "content2"},
                {"file_name": "doc3.pdf", "text": "content3"},
            ]
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(cli, ["batch", str(pdf_directory)])
            assert result.exit_code == 0

            output_data = json.loads(result.output)
            assert isinstance(output_data, list)
            assert len(output_data) == 3

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_batch_command_recursive(self, temp_dir):
        """Test batch command with recursive flag."""
        # Create nested structure
        sub_dir = temp_dir / "subdir"
        sub_dir.mkdir()

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_path = sub_dir / "nested.pdf"
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.drawString(100, 750, "Nested PDF")
        c.save()

        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_directory.return_value = [
                {"file_name": "nested.pdf", "text": "Nested PDF content"}
            ]
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(cli, ["batch", str(temp_dir), "--recursive"])
            assert result.exit_code == 0

            output_data = json.loads(result.output)
            assert len(output_data) == 1
            assert "nested.pdf" in output_data[0]["file_name"]

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_batch_command_empty_directory(self, empty_directory):
        """Test batch command on empty directory."""
        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_directory.return_value = []
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(cli, ["batch", str(empty_directory)])
            assert result.exit_code == 0
            assert "No PDF files found" in result.output

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_info_command(self, sample_pdf):
        """Test info command."""
        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.get_file_info.return_value = {
                "file_name": sample_pdf.name,
                "file_size": 1234,
                "page_count": 1,
                "title": sample_pdf.stem,
                "author": None,
            }
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(cli, ["info", str(sample_pdf)])
            assert result.exit_code == 0
            assert "PDF File Information" in result.output
            assert sample_pdf.stem in result.output

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_page_command(self, sample_pdf):
        """Test page extraction command."""
        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.extractor.extract_page_text.return_value = (
                "Page 1 content from sample PDF document"
            )
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(cli, ["page", str(sample_pdf), "0"])
            assert result.exit_code == 0
            assert "Page 1 content" in result.output

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_page_command_second_page(self, sample_pdf):
        """Test extracting second page."""
        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.extractor.extract_page_text.return_value = "Page 2 content"
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(cli, ["page", str(sample_pdf), "1"])
            assert result.exit_code == 0
            assert "Page 2 content" in result.output

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_page_command_invalid_page(self, sample_pdf):
        """Test page command with invalid page number."""
        from ingest_pdf.exceptions import PDFExtractionError

        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.extractor.extract_page_text.side_effect = PDFExtractionError(
                "Page not found"
            )
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(cli, ["page", str(sample_pdf), "999"])
            assert result.exit_code == 1
            assert "Error" in result.output

    @patch.dict(os.environ, {"LLAMA_CLOUD_API_KEY": "test-api-key"})
    def test_verbose_flag(self, sample_pdf):
        """Test verbose logging flag."""
        with patch("ingest_pdf.main.PDFProcessor") as mock_processor_class:
            mock_processor = Mock()
            mock_processor.extract_text_only.return_value = "Verbose test content"
            mock_processor_class.return_value = mock_processor

            result = self.runner.invoke(
                cli, ["--verbose", "process", str(sample_pdf), "--text-only"]
            )
            assert result.exit_code == 0
