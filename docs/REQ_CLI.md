# CLI (pdf_extract/cli.py) Requirement

This cli is an entry point to the pdf ingesting, extraction, and storing process.

## The workflow

1. Inbox-Monitor - On start
    - Read configuration
    - Access the preconfigured location (inbox) from configuration
    - Check if there are any files to process in the inbox.
    - If not files found, sleep for pre-configured time intervals
    - If files found, create a job list for each of the files (include file in job detail).
    - Go to sleep for preconfigured time interval

2. Ingestion Job - On start
    - Read configuration
    - Create a watch for monitoring incoming jobs at pre-configured location.
    - 


