# Initialize the cli
from datetime import datetime, UTC, timezone
from dateutil import tz
import time
import os
import hashlib


from config import settings
from pdf_ingestion.models import PdfIngestionRequest
from utils.context import RunContext
from utils.logger import json_setup_logger

CFG = settings()
_RUN_ID = RunContext.create(length=20, dry_run=False, verbose=False).run_id
_LOG_NAME = f"pdf_scheduler"
_logger = json_setup_logger(job_name=f"{_LOG_NAME}", log_name=_LOG_NAME)

_LOCAL_NOW = datetime.now(tz.tzlocal())
_UTC_FROM_LOCAL = _LOCAL_NOW.astimezone(timezone.utc)


class PdfExtractCli:
    def __init__(self):
        self.logger = _logger 
        self._inbox = CFG['input']['dir']
        self._output_jsonl = CFG['output']['jsonl_dir']
        self._output_markdown = CFG['output']['markdown_dir']
        self._processed = CFG['processed']['dir']
        self._quarantine = CFG['quarantine']['dir']
        self._job_file = CFG['job']['job_file']

        self._utc_now = _UTC_FROM_LOCAL
        self._local_now = _LOCAL_NOW
        print(self._utc_now, self._local_now)

    
    def run(self):
        try:
            self.logger.info("Starting PDF extraction workflow", extra={"datetime": self._utc_now})

            # Create PdfExtractModel with run context
            from pdf_ingestion.ingest import ingest

            ## Check self._inbox folder for any files
            ## if inbox not empty, get the entire file list
            self.logger.info("Checking inbox for any files", extra={"datetime": self._utc_now})
            if os.listdir(self._inbox):
                file_list = os.listdir(self._inbox)
                self.logger.info("Number of files found: {len(file_list)}", extra={"datetime": self._utc_now})

                ## For each file in the list, perform the ingestion process
                for file in file_list:
                    run_id = RunContext.create(length=20, dry_run=False, verbose=False).run_id
                    
                    self.logger.info("Performing ingestion process for file: %s", file, extra={"run_id": run_id})

                    ## create file name based on jsonl_file_format
                    ## TODO: concatinate utc datetime to file name
                    jsonl_file_name = CFG['output']['jsonl_file_format'].format(stem=file, cuid=run_id)
                    markdown_file_name = CFG['output']['markdown_file_format'].format(stem=file, cuid=run_id)

                    print(jsonl_file_name)
                    print(markdown_file_name)

                    ## Create model with proper file paths based on configuration
                    req = PdfIngestionRequest(
                        PdfInput=file,
                        JsonOutput=jsonl_file_name,
                        MarkdownOutput=markdown_file_name)
                    
                    ingestor = ingest(run_id)
                    
                    ## Run the extraction workflow
                    ingestor.run(req)

                self.logger.info("PDFExtractor initialized, starting extraction", 
                            extra={"run_id": run_id})
                
                # Run the extraction workflow
                #extractor.run()
                
            else:
                self.logger.info("Inbox is empty", extra={"datetime": self._utc_now})
                file_list = []

            self.logger.info("PDF extraction workflow completed successfully", extra={"datetime": self._utc_now})


        except Exception as e:
            self.logger.error("PDF extraction workflow failed", 
                           extra={"datetime": self._utc_now, "error": str(e), "error_type": type(e).__name__})
            raise

def main():
    _logger.info(f"Extract CLI starting, App version: {CFG['version']['app_version']}", 
               extra={"app_version": CFG['version']['app_version']})
   
    try:
        cli = PdfExtractCli()

        ## Loop until next cycle.
        while True:
            cli.run()
            print("Waiting for next cycle...")
            time.sleep(10)

    except Exception as e:
        _logger.error("PDF Extract CLI failed", 
                   extra={"datetime": _UTC_FROM_LOCAL, "error": str(e), "error_type": type(e).__name__})
        raise

    _logger.info("Extract CLI completed successfully")

if __name__ == "__main__":
    main()




