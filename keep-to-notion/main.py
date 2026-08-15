"""진입점: 초기 1회 동기화 후 주기적으로 재실행."""
import logging
import time
from datetime import datetime

import schedule

import config
from keep_client import KeepClient
from notion_wrapper import NotionSync
from sync import run_sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)
logger = logging.getLogger(__name__)


def sync_job(keep: KeepClient, notion: NotionSync) -> None:
    created, archived = run_sync(keep, notion)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    logger.info(
        "[%s] 동기화 완료: 신규 %d건, 아카이브 %d건", timestamp, created, archived
    )


def main() -> None:
    keep = KeepClient(config.GOOGLE_EMAIL, config.GOOGLE_MASTER_TOKEN)
    notion = NotionSync(config.NOTION_TOKEN, config.NOTION_DATABASE_ID)

    sync_job(keep, notion)

    schedule.every(config.SYNC_INTERVAL_MINUTES).minutes.do(sync_job, keep, notion)
    logger.info("스케줄러 시작: %d분마다 동기화", config.SYNC_INTERVAL_MINUTES)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
