

# Modele to provide extraction class to operating a specific extraciong operation

from pydantic import BaseModel

"""
PdfInput: file path to the pdf file
JsonOutput: file path to the json file
MarkdownOutput: file path to the markdown file
"""

class PdfExtractModel(BaseModel):
    PdfInput: str
    JsonOutput: str
    MarkdownOutput: str

class PdfExtractResult(BaseModel):
    PdfInput: str
    JsonOutput: str
    MarkdownOutput: str

