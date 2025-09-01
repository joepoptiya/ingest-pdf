# Initialize the cli

from config import settings
from utils.context import RunContext
from utils.logger import json_setup_logger

from pdf_extract.init import PDFExtractor


CFG = settings()


class PdfExtractCli:
    def __init__(self):

        pass
    
    def run(self):
        pass



def main():
    context = RunContext.create(dry_run=False, verbose=True)
    print(f"Run ID: {context.run_id}")
    print(CFG['version']['app_version'])
    cli = PdfExtractCli()
    cli.run()
    pass

if __name__ == "__main__":
    main()




