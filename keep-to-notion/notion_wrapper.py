"""Notion API 래퍼."""
import logging
import time

from notion_client import Client
from notion_client.errors import APIResponseError

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
RICH_TEXT_MAX_LEN = 2000

PROP_TITLE = "제목"
PROP_TEXT = "내용"
PROP_KEEP_ID = "Keep_ID"
PROP_COLOR = "색상"
PROP_LABELS = "라벨"
PROP_PINNED = "고정됨"
PROP_CREATED = "생성일"
PROP_MODIFIED = "수정일"
PROP_STATUS = "상태"
PROP_URL = "URL"

STATUS_ACTIVE = "활성"
STATUS_ARCHIVED = "아카이브"


def _retry(func, *args, **kwargs):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return func(*args, **kwargs)
        except APIResponseError as exc:
            last_error = exc
            logger.warning(
                "Notion API 호출 실패 (시도 %d/%d): %s", attempt, MAX_RETRIES, exc
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    logger.error("Notion API 호출이 %d회 재시도 후에도 실패했습니다: %s", MAX_RETRIES, last_error)
    raise last_error


def _rich_text(content: str) -> list[dict]:
    trimmed = (content or "")[:RICH_TEXT_MAX_LEN]
    if not trimmed:
        return []
    return [{"text": {"content": trimmed}}]


def _iso(dt) -> str | None:
    if dt is None:
        return None
    return dt.isoformat()


class NotionSync:
    def __init__(self, token: str, database_id: str):
        self._client = Client(auth=token)
        self._database_id = database_id

    def get_all_keep_ids(self) -> set[str]:
        """DB 전체를 페이지네이션 조회해 Keep_ID 값 set 반환."""
        ids: set[str] = set()
        start_cursor = None
        while True:
            response = _retry(
                self._client.databases.query,
                database_id=self._database_id,
                start_cursor=start_cursor,
                page_size=100,
            )
            for page in response["results"]:
                keep_id = self._extract_keep_id(page)
                if keep_id:
                    ids.add(keep_id)
            if response.get("has_more"):
                start_cursor = response["next_cursor"]
            else:
                break
        return ids

    def get_active_pages(self) -> list[dict]:
        """상태가 '활성'인 페이지들을 {id, keep_id} 형태로 반환."""
        pages = []
        start_cursor = None
        while True:
            response = _retry(
                self._client.databases.query,
                database_id=self._database_id,
                start_cursor=start_cursor,
                page_size=100,
                filter={
                    "property": PROP_STATUS,
                    "select": {"equals": STATUS_ACTIVE},
                },
            )
            for page in response["results"]:
                pages.append(
                    {
                        "id": page["id"],
                        "keep_id": self._extract_keep_id(page),
                    }
                )
            if response.get("has_more"):
                start_cursor = response["next_cursor"]
            else:
                break
        return pages

    def create_page(self, data: dict) -> dict:
        properties = {
            PROP_TITLE: {"title": [{"text": {"content": data["title"]}}]},
            PROP_TEXT: {"rich_text": _rich_text(data["text"])},
            PROP_KEEP_ID: {"rich_text": _rich_text(data["keep_id"])},
            PROP_COLOR: {"select": {"name": data["color"]}},
            PROP_LABELS: {"multi_select": [{"name": name} for name in data["labels"]]},
            PROP_PINNED: {"checkbox": data["pinned"]},
            PROP_STATUS: {"select": {"name": data["status"]}},
        }

        created = _iso(data.get("created"))
        modified = _iso(data.get("modified"))
        if created:
            properties[PROP_CREATED] = {"date": {"start": created}}
        if modified:
            properties[PROP_MODIFIED] = {"date": {"start": modified}}
        if data.get("url"):
            properties[PROP_URL] = {"url": data["url"]}

        return _retry(
            self._client.pages.create,
            parent={"database_id": self._database_id},
            properties=properties,
        )

    def archive_page(self, page_id: str) -> dict:
        return _retry(
            self._client.pages.update,
            page_id=page_id,
            properties={PROP_STATUS: {"select": {"name": STATUS_ARCHIVED}}},
        )

    @staticmethod
    def _extract_keep_id(page: dict) -> str | None:
        rich_text = page["properties"].get(PROP_KEEP_ID, {}).get("rich_text", [])
        if not rich_text:
            return None
        return rich_text[0]["plain_text"]
