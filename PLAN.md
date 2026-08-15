# PLAN.md

이 프로젝트(`Keep2Notion`)의 유일한 진실 공급원(Single Source of Truth). 세션 시작 시 항상 이 문서를 먼저 읽는다.

## 프로젝트 개요

Google Keep 메모를 `gkeepapi`로 읽어 Notion 데이터베이스에 주기적으로 동기화한다. Notion에는
Keep 메모가 갤러리 뷰로 노출되며, Claude Notion MCP로 Keep 데이터를 간접 활용하는 것이 목적.

```
[Google Keep] --gkeepapi--> [Python 스크립트] --Notion API--> [Notion DB]
```

구현 위치: `keep-to-notion/` (파일 구조는 `keep-to-notion/README.md` 참고)

## 현재 개발 브랜치

- `claude/keep-notion-sync-script-cky4og` (2026-08-15 기준)

## Notion DB 스키마

| 속성명 | 타입 | Keep 매핑 |
|---|---|---|
| `제목` | Title | 메모 첫 줄 또는 제목 |
| `내용` | Text | 메모 본문 |
| `Keep_ID` | Text | 메모 고유 ID (중복 방지 키) |
| `색상` | Select | Keep 색상 (한글 매핑, `mapper.py`의 `COLOR_MAP`) |
| `라벨` | Multi-select | Keep 라벨들 |
| `고정됨` | Checkbox | Keep 핀 여부 |
| `생성일` | Date | Keep 생성 타임스탬프 |
| `수정일` | Date | Keep 수정 타임스탬프 |
| `상태` | Select | `활성` / `아카이브` |
| `URL` | URL | 클리핑된 링크 (있을 경우) |

## 동기화 흐름

1. Notion DB 전체 조회 → 기존 `Keep_ID` set 수집 (`notion_wrapper.get_all_keep_ids`)
2. Keep 전체 노트 조회, 삭제/휴지통 노트 제외 (`keep_client.get_all_notes`)
3. Notion에 없는 `Keep_ID`만 신규 페이지 생성
4. Notion `상태 = 활성` 페이지 중 Keep에 더 이상 없는 `Keep_ID` → `상태 = 아카이브`로 전환
5. `main.py`가 최초 1회 즉시 실행 후 `SYNC_INTERVAL_MINUTES` 주기로 반복

## 완료된 작업

| 날짜 | 작업 내용 |
|---|---|
| 2026-08-15 | `keep-to-notion/` 초기 구현 (keep_client, notion_wrapper, mapper, sync, main, create_database, get_master_token, README) |
| 2026-08-15 | `CLAUDE.md` / `PLAN.md` 작업 규칙 및 진실 공급원 문서 추가 |

## 남은 작업

- [ ] 실제 Google 계정 / Notion DB로 end-to-end 동작 검증 (README "검증 방법" 참고)
- [ ] Notion DB 갤러리 뷰 생성 및 확인
- [ ] (선택) PLAN.md 수정 시 자동 커밋하는 Stop 훅 실제 구성 여부 결정

<!-- sync-plan.sh 훅 테스트: 2026-08-15T01:19:20Z -->
