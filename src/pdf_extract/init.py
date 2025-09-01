import os
import json
import sys
from pathlib import Path
from datetime import datetime
from llama_parse import LlamaParse
from dotenv import load_dotenv
import nest_asyncio
from cuid2 import Cuid
from utils.logger import json_setup_logger

from config import settings, reload_settings
from models import PdfExtractModel

CFG = settings()
reload_settings()

load_dotenv()
nest_asyncio.apply()

#RUN_ID: Cuid = Cuid(length=10).generate()

class PDFExtractor:
    def __init__(self, model: PdfExtractModel):
        self.RUN_ID: Cuid = Cuid(length=10).generate()
        self.logger = json_setup_logger(f"pdf_extract_{self.RUN_ID}")
        self.inbox = CFG['input']['dir']
        print(self.inbox)
        self.parser = LlamaParse(
            verbose=CFG['llamaparse']['verbose'],
            premium_mode=CFG['llamaparse']['premium_mode']
        )
        self._INPUT_DIR = Path(CFG['input']['dir'])
        self._OUTPUT_JSON_DIR = Path(CFG['output']['jsonl_dir'])
        self._OUTPUT_MARKDOWN_DIR = Path(CFG['output']['markdown_dir'])
        self._init()

    def _init(self):
        self._INPUT_DIR.mkdir(parents=True, exist_ok=True)
        self._OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)
        self._OUTPUT_MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

    def run(self):
        ## Update the job record
        ## Ingest the pdf file
        ## Store the json file output
        ## Store the markdown file output
        ## Store the processed file in the processed directory
        ## If failed, Store the failed file in the quarantine directory
        ## Store the run file
        pass

    def _ingest(self):
        pass
    
    def _store_json(self):
        pass
    
    def _store_markdown(self):
        pass

    def _store_processed(self):
        pass
    
    def _store_quarantine(self):
        pass

    def _store_run(self):
        pass