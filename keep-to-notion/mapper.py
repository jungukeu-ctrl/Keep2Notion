"""Keep 노트 dict -> Notion 페이지 속성 변환."""
import re

COLOR_MAP = {
    "DEFAULT": "기본",
    "RED": "빨강",
    "ORANGE": "주황",
    "YELLOW": "노랑",
    "GREEN": "초록",
    "TEAL": "청록",
    "BLUE": "파랑",
    "CERULEAN": "하늘",
    "PURPLE": "보라",
    "PINK": "분홍",
    "BROWN": "갈색",
    "GRAY": "회색",
}

URL_PATTERN = re.compile(r"https?://\S+")

TITLE_MAX_LEN = 30


def _derive_title(title: str, text: str) -> str:
    if title:
        return title
    first_line = (text or "").strip().splitlines()[0] if text else ""
    if len(first_line) > TITLE_MAX_LEN:
        return first_line[:TITLE_MAX_LEN] + "..."
    return first_line or "(제목 없음)"


def _extract_url(note: dict) -> str | None:
    if note.get("url"):
        return note["url"]
    match = URL_PATTERN.search(note.get("text") or "")
    return match.group(0) if match else None


def convert(note: dict, status: str = "활성") -> dict:
    """Keep 노트 dict를 notion_client.create_page 가 사용할 속성 dict로 변환."""
    return {
        "keep_id": note["id"],
        "title": _derive_title(note.get("title", ""), note.get("text", "")),
        "text": note.get("text") or "",
        "color": COLOR_MAP.get(note.get("color", "DEFAULT"), "기본"),
        "labels": note.get("labels", []),
        "pinned": bool(note.get("pinned")),
        "created": note.get("created"),
        "modified": note.get("modified"),
        "status": status,
        "url": _extract_url(note),
    }
