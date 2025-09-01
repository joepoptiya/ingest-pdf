from pathlib import Path

import nest_asyncio
from dotenv import load_dotenv
from llama_parse import LlamaParse

from .config import reload_settings, settings
from .models import PdfExtractModel

CFG = settings()
reload_settings()

load_dotenv()
nest_asyncio.apply()

_INPUT_DIR = Path(CFG['input']['dir'])
_OUTPUT_JSON_DIR = Path(CFG['output']['jsonl_dir'])
_OUTPUT_MARKDOWN_DIR = Path(CFG['output']['markdown_dir'])

_OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)
_OUTPUT_MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
_INPUT_DIR.mkdir(parents=True, exist_ok=True)


class PDFExtractor:
    def __init__(self, model: PdfExtractModel):
        self.parser = LlamaParse(
            verbose=CFG['llamaparse']['verbose'],
            premium_mode=CFG['llamaparse']['premium_mode']
        )
