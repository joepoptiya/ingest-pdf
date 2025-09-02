import os
import json
import sys
from pathlib import Path
from datetime import datetime
from llama_parse import LlamaParse
from dotenv import load_dotenv
import nest_asyncio
from utils.logger import json_setup_logger
from utils.context import RunContext

from config import settings, reload_settings
from pdf_extract.models import PdfExtractModel

CFG = settings()
reload_settings()

load_dotenv()
nest_asyncio.apply()

class PDFExtractor:
    def __init__(self, model: PdfExtractModel, context: RunContext = None):
        # Use provided context or create new one
        self.context = context if context else RunContext.create(dry_run=False, verbose=True)
        self.RUN_ID = self.context.run_id  # Use context run_id for consistency
        self.logger = json_setup_logger(f"pdf_extract_{self.RUN_ID}")
        self.model = model
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
        self.logger.info("PDFExtractor initialized", 
                        extra={"run_id": self.RUN_ID, "inbox": str(self.inbox)})

    def _init(self):
        self._INPUT_DIR.mkdir(parents=True, exist_ok=True)
        self._OUTPUT_JSON_DIR.mkdir(parents=True, exist_ok=True)
        self._OUTPUT_MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

    def run(self):
        self.logger.info("Starting PDF extraction workflow", extra={"run_id": self.RUN_ID})
        
        try:
            # Update the job record
            self.logger.info("Updating job record", extra={"run_id": self.RUN_ID})
            self._update_job_record()
            
            # Ingest the pdf file
            self.logger.info("Ingesting PDF file", extra={"run_id": self.RUN_ID})
            self._ingest()
            
            # Store the json file output
            self.logger.info("Storing JSON output", extra={"run_id": self.RUN_ID})
            self._store_json()
            
            # Store the markdown file output
            self.logger.info("Storing Markdown output", extra={"run_id": self.RUN_ID})
            self._store_markdown()
            
            # Store the processed file in the processed directory
            self.logger.info("Moving file to processed directory", extra={"run_id": self.RUN_ID})
            self._store_processed()
            
            # Store the run file
            self.logger.info("Storing run metadata", extra={"run_id": self.RUN_ID})
            self._store_run()
            
            self.logger.info("PDF extraction workflow completed successfully", 
                           extra={"run_id": self.RUN_ID})
            
        except Exception as e:
            self.logger.error("PDF extraction workflow failed, moving to quarantine", 
                            extra={"run_id": self.RUN_ID, "error": str(e), "error_type": type(e).__name__})
            # If failed, Store the failed file in the quarantine directory
            try:
                self._store_quarantine()
            except Exception as quarantine_error:
                self.logger.error("Failed to quarantine file", 
                                extra={"run_id": self.RUN_ID, "quarantine_error": str(quarantine_error)})
            raise

    def _update_job_record(self):
        # TODO: Implement job record update
        self.logger.info("Job record updated", extra={"run_id": self.RUN_ID})
        pass
    
    def _ingest(self):
        # TODO: Implement PDF ingestion using LlamaParse
        self.logger.info("PDF ingestion completed", extra={"run_id": self.RUN_ID})
        pass
    
    def _store_json(self):
        # TODO: Implement JSON storage
        self.logger.info("JSON output stored", extra={"run_id": self.RUN_ID, "output_dir": str(self._OUTPUT_JSON_DIR)})
        pass
    
    def _store_markdown(self):
        # TODO: Implement Markdown storage
        self.logger.info("Markdown output stored", extra={"run_id": self.RUN_ID, "output_dir": str(self._OUTPUT_MARKDOWN_DIR)})
        pass

    def _store_processed(self):
        # TODO: Implement processed file storage
        self.logger.info("File moved to processed directory", extra={"run_id": self.RUN_ID})
        pass
    
    def _store_quarantine(self):
        # TODO: Implement quarantine file storage
        self.logger.info("File moved to quarantine directory", extra={"run_id": self.RUN_ID})
        pass

    def _store_run(self):
        # TODO: Implement run metadata storage
        self.logger.info("Run metadata stored", extra={"run_id": self.RUN_ID})
        pass