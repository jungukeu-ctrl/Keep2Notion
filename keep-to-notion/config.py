"""환경 설정값 로드."""
import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"필수 환경변수가 설정되지 않았습니다: {name}")
    return value


GOOGLE_EMAIL = _require("GOOGLE_EMAIL")
GOOGLE_MASTER_TOKEN = _require("GOOGLE_MASTER_TOKEN")
NOTION_TOKEN = _require("NOTION_TOKEN")
NOTION_DATABASE_ID = _require("NOTION_DATABASE_ID")
SYNC_INTERVAL_MINUTES = int(os.environ.get("SYNC_INTERVAL_MINUTES", "60"))
