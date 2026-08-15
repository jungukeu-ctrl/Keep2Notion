"""gkeepapi 래퍼: Google Keep 노트 읽기."""
import logging

import gkeepapi

logger = logging.getLogger(__name__)


class KeepClient:
    def __init__(self, email: str, master_token: str):
        self._keep = gkeepapi.Keep()
        self._keep.resume(email, master_token)
        logger.info("Google Keep 인증 완료: %s", email)

    def get_all_notes(self) -> list[dict]:
        """삭제되지 않은 전체 노트를 dict 리스트로 반환."""
        notes = []
        for note in self._keep.all():
            if note.deleted or note.trashed:
                continue
            notes.append(self._to_dict(note))
        return notes

    @staticmethod
    def _to_dict(note) -> dict:
        labels = [label.name for label in note.labels.all()]
        urls = [link.url for link in note.annotations.links]

        return {
            "id": note.id,
            "title": note.title,
            "text": note.text,
            "color": note.color.name,
            "labels": labels,
            "pinned": note.pinned,
            "created": note.timestamps.created,
            "modified": note.timestamps.edited,
            "url": urls[0] if urls else None,
        }
