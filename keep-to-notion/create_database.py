"""Notion DB를 스키마에 맞춰 자동 생성하는 1회성 스크립트.

사용법:
    python create_database.py <상위 페이지 ID>

생성된 데이터베이스의 ID가 출력되며, 이 값을 .env의 NOTION_DATABASE_ID에 넣으면 된다.
"""
import os
import sys

from dotenv import load_dotenv
from notion_client import Client

from notion_wrapper import (
    PROP_COLOR,
    PROP_CREATED,
    PROP_KEEP_ID,
    PROP_LABELS,
    PROP_MODIFIED,
    PROP_PINNED,
    PROP_STATUS,
    PROP_TEXT,
    PROP_TITLE,
    PROP_URL,
    STATUS_ACTIVE,
    STATUS_ARCHIVED,
)
from mapper import COLOR_MAP

load_dotenv()

COLOR_OPTIONS = [{"name": name} for name in COLOR_MAP.values()]


def create_database(token: str, parent_page_id: str) -> dict:
    client = Client(auth=token)
    return client.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "Keep Sync"}}],
        properties={
            PROP_TITLE: {"title": {}},
            PROP_TEXT: {"rich_text": {}},
            PROP_KEEP_ID: {"rich_text": {}},
            PROP_COLOR: {"select": {"options": COLOR_OPTIONS}},
            PROP_LABELS: {"multi_select": {}},
            PROP_PINNED: {"checkbox": {}},
            PROP_CREATED: {"date": {}},
            PROP_MODIFIED: {"date": {}},
            PROP_STATUS: {
                "select": {
                    "options": [
                        {"name": STATUS_ACTIVE},
                        {"name": STATUS_ARCHIVED},
                    ]
                }
            },
            PROP_URL: {"url": {}},
        },
    )


def main() -> None:
    if len(sys.argv) != 2:
        print("사용법: python create_database.py <상위 페이지 ID>")
        sys.exit(1)

    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("NOTION_TOKEN 환경변수가 설정되지 않았습니다. .env를 확인하세요.")
        sys.exit(1)

    parent_page_id = sys.argv[1]
    database = create_database(token, parent_page_id)
    print("데이터베이스 생성 완료.")
    print(f"NOTION_DATABASE_ID={database['id']}")


if __name__ == "__main__":
    main()
