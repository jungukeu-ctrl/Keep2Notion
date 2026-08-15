"""Keep <-> Notion 동기화 로직 (신규 추가 / 아카이브)."""
import logging

import mapper
from keep_client import KeepClient
from notion_wrapper import NotionSync

logger = logging.getLogger(__name__)


def run_sync(keep: KeepClient, notion: NotionSync) -> tuple[int, int]:
    """동기화 1회 실행. (신규 추가 건수, 아카이브 처리 건수) 반환."""
    existing_ids = notion.get_all_keep_ids()
    keep_notes = keep.get_all_notes()

    created_count = 0
    for note in keep_notes:
        if note["id"] in existing_ids:
            continue
        notion.create_page(mapper.convert(note))
        created_count += 1
        logger.info("Notion 페이지 생성: %s", note["id"])

    keep_ids = {note["id"] for note in keep_notes}
    archived_count = 0
    for page in notion.get_active_pages():
        if page["keep_id"] and page["keep_id"] not in keep_ids:
            notion.archive_page(page["id"])
            archived_count += 1
            logger.info("Notion 페이지 아카이브: %s", page["keep_id"])

    return created_count, archived_count
