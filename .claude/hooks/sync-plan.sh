#!/usr/bin/env bash
# Stop 훅: PLAN.md 변경 시 자동 커밋 + main 직접 push (CLAUDE.md 규칙 5의 명시적 예외)
# 실패해도 세션 Stop 자체를 막지 않도록 항상 exit 0으로 종료한다.
set -u

LOG=/tmp/sync-plan.log

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$REPO_ROOT" || exit 0

[ -f PLAN.md ] || exit 0

# 워킹트리/인덱스 어느 쪽에도 PLAN.md 변경이 없으면 조용히 종료
if git diff --quiet -- PLAN.md && git diff --cached --quiet -- PLAN.md; then
  exit 0
fi

git add PLAN.md

if ! git commit -m "auto: sync PLAN.md via Stop hook" -- PLAN.md >"$LOG" 2>&1; then
  echo "[sync-plan] PLAN.md 자동 커밋 실패, 건너뜁니다. 로그: $LOG" >&2
  exit 0
fi

if ! git push origin HEAD:main >>"$LOG" 2>&1; then
  echo "[sync-plan] PLAN.md는 커밋됐지만 main push는 실패했습니다 (세션은 계속 진행). 로그: $LOG" >&2
  exit 0
fi

echo '{"systemMessage": "PLAN.md 변경사항을 커밋하고 main에 동기화했습니다."}'
exit 0
