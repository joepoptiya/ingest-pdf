
from config import settings, reload_settings


CFG = settings()

def main() -> None:
    print(f"CFG: {CFG['version']['app_version']}")

if __name__ == "__main__":
    main()