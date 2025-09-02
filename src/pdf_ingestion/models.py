

# Modele to provide extraction class to operating a specific extraciong operation

from pydantic import BaseModel

"""
PdfInput: file path to the pdf file
JsonOutput: file path to the json file
MarkdownOutput: file path to the markdown file
"""

class PdfIngestionRequest(BaseModel):
    PdfInput: str
    JsonOutput: str
    MarkdownOutput: str

class PdfIngestionResult(BaseModel):
    PdfInput: str
    JsonOutput: str
    MarkdownOutput: str

