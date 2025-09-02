from cuid2 import Cuid

from config import settings
from utils.context import RunContext
from utils.logger import json_setup_logger

CFG = settings()

CUID_GENERATOR: Cuid = Cuid(length=20)

def main():
  context = RunContext.create(length=32, verbose=True)
  logger = json_setup_logger(job_name=f"{context.run_id}", log_name=f"_test_cuid_{context.run_id}")
  logger.info("Test CUID starting", extra={"run_id": context.run_id})
  my_cuid: str = CUID_GENERATOR.generate()
  next_cuid: str = CUID_GENERATOR.generate()
  print(f"My CUID: {my_cuid}")
  print(f"Next CUID: {next_cuid}")

if __name__ == "__main__":
  main()
