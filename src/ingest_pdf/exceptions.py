"""Custom exceptions for PDF processing."""


class PDFProcessingError(Exception):
    """Base exception for PDF processing errors."""

    pass


class PDFNotFoundError(PDFProcessingError):
    """Raised when a PDF file cannot be found."""

    pass


class PDFReadError(PDFProcessingError):
    """Raised when a PDF file cannot be read."""

    pass


class PDFExtractionError(PDFProcessingError):
    """Raised when text extraction from PDF fails."""

    pass
