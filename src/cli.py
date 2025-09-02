# Initialize the cli

from config import settings
from utils.context import RunContext
from utils.logger import json_setup_logger

from pdf_extract.init import PDFExtractor


CFG = settings()


class PdfExtractCli:
    def __init__(self, context: RunContext):
        self.context = context
        self.logger = json_setup_logger(f"pdf_extract_cli_{context.run_id}")
        self.logger.info("PdfExtractCli initialized", extra={"run_id": context.run_id})
    
    def run(self):
        self.logger.info("Starting PDF extraction workflow", extra={"run_id": self.context.run_id})
        
        try:
            # Create PdfExtractModel with run context
            from pdf_extract.models import PdfExtractModel
            # TODO: Create model with proper file paths based on configuration
            model = PdfExtractModel(
                PdfInput="",  # Will be set during file processing
                JsonOutput="",  # Will be set during file processing
                MarkdownOutput=""  # Will be set during file processing
            )
            
            # Initialize PDFExtractor with context to ensure consistent run_id
            extractor = PDFExtractor(model, context=self.context)
            
            self.logger.info("PDFExtractor initialized, starting extraction", 
                           extra={"run_id": self.context.run_id})
            
            # Run the extraction workflow
            extractor.run()
            
            self.logger.info("PDF extraction workflow completed successfully", 
                           extra={"run_id": self.context.run_id})
            
        except Exception as e:
            self.logger.error("PDF extraction workflow failed", 
                           extra={"run_id": self.context.run_id, "error": str(e), "error_type": type(e).__name__})
            raise



def main():
    context = RunContext.create(dry_run=False, verbose=True)
    logger = json_setup_logger(f"pdf_extract_main_{context.run_id}")
    
    logger.info("PDF Extract CLI starting", 
               extra={"run_id": context.run_id, "app_version": CFG['version']['app_version']})
    
    print(f"Run ID: {context.run_id}")
    print(CFG['version']['app_version'])
    
    try:
        cli = PdfExtractCli(context)
        cli.run()
        logger.info("PDF Extract CLI completed successfully", extra={"run_id": context.run_id})
    except Exception as e:
        logger.error("PDF Extract CLI failed", 
                   extra={"run_id": context.run_id, "error": str(e), "error_type": type(e).__name__})
        raise

if __name__ == "__main__":
    main()




