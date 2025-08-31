"""PDF ingestion and processing package."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .exceptions import PDFNotFoundError, PDFProcessingError
from .extractor import PDFExtractor
from .processor import PDFProcessor

__all__ = [
    "PDFProcessor",
    "PDFExtractor",
    "PDFProcessingError",
    "PDFNotFoundError",
]
