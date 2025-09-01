from cuid2 import Cuid

from config import settings

CFG = settings()

CUID_GENERATOR: Cuid = Cuid(length=10)

def main():
  my_cuid: str = CUID_GENERATOR.generate()
  next_cuid: str = CUID_GENERATOR.generate()
  print(f"My CUID: {my_cuid}")
  print(f"Next CUID: {next_cuid}")

if __name__ == "__main__":
  main()
