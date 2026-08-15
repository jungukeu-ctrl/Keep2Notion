# Keep → Notion 동기화

Google Keep 메모를 주기적으로 읽어 Notion 데이터베이스에 동기화합니다. Keep에는 공개 API가
없어 비공식 라이브러리 [`gkeepapi`](https://github.com/kiwiz/gkeepapi)를 사용합니다.

```
[Google Keep] --gkeepapi--> [Python 스크립트] --Notion API--> [Notion DB]
```

- Notion DB에 없는 Keep 메모만 신규 추가 (Keep_ID로 중복 방지)
- Keep에서 삭제된 메모는 Notion에서 `상태 = 아카이브` 처리
- `schedule` 라이브러리로 주기 실행 (기본 60분)

## 설치

```bash
cd keep-to-notion
pip install -r requirements.txt
cp .env.example .env
```

## 1. Notion 준비

1. https://www.notion.so/my-integrations 에서 Internal Integration을 만들고 토큰을 발급받습니다.
2. Notion에서 이 스크립트가 DB를 생성할 상위 페이지를 만들고, 방금 만든 Integration을
   해당 페이지에 연결(Connect)합니다.
3. 상위 페이지 ID를 확인한 뒤 DB 자동 생성 스크립트를 실행합니다.

```bash
python create_database.py <상위 페이지 ID>
```

출력된 `NOTION_DATABASE_ID` 값과 1번의 토큰을 `.env`에 채워 넣습니다.

생성된 DB는 다음 속성을 가집니다: `제목`(Title), `내용`(Text), `Keep_ID`(Text, 중복 방지 키),
`색상`(Select), `라벨`(Multi-select), `고정됨`(Checkbox), `생성일`/`수정일`(Date),
`상태`(Select: 활성/아카이브), `URL`.

DB 페이지에서 뷰를 **갤러리 뷰**로 전환하면 포스트잇 형태로 볼 수 있습니다.

## 2. Google Master Token 획득 방법

gkeepapi는 일반 비밀번호 로그인이 Google에 의해 차단됩니다. Master Token 방식을 사용해야
하며, 최초 1회만 발급받으면 이후 재로그인이 필요 없습니다.

1. 이미 `pip install -r requirements.txt`로 `gpsoauth`가 설치되어 있습니다.
2. 브라우저(시크릿 창 권장)에서 아래 주소로 접속해 사용할 Google 계정으로 로그인합니다.
   ```
   https://accounts.google.com/EmbeddedSetup
   ```
3. 로그인 완료 후 개발자 도구(F12) → Network 탭을 열고, `oauth_token` 파라미터가 포함된
   요청을 찾습니다 (`oauth2_4/`로 시작하는 값). 이 값을 복사합니다.
   - 계정에 2단계 인증이 걸려 있다면 로그인 과정에서 함께 처리됩니다.
4. 토큰 교환 스크립트를 실행합니다.
   ```bash
   python get_master_token.py
   ```
   이메일과 3번에서 복사한 `oauth_token`을 입력하면 Master Token이 출력됩니다.
5. 출력된 값을 `.env`의 `GOOGLE_MASTER_TOKEN`에 저장합니다.

> Master Token은 비밀번호와 동등한 민감 정보입니다. `.env`는 반드시 `.gitignore`에
> 포함된 상태로 유지하고, 절대 커밋하거나 공유하지 마세요.

## 3. 실행

```bash
python main.py
```

최초 실행 시 즉시 1회 동기화하고, 이후 `.env`의 `SYNC_INTERVAL_MINUTES` 주기로 반복
실행합니다. 로그는 다음 형식으로 출력됩니다.

```
[2026-08-15 09:00] 동기화 완료: 신규 3건, 아카이브 1건
```

### Windows에서 상시 실행

- 터미널을 계속 열어두고 `python main.py`를 실행하거나
- Windows 작업 스케줄러에 `python main.py`를 로그온 시 1회 실행하도록 등록해 상시
  구동시킬 수 있습니다.

## 파일 구조

```
keep-to-notion/
├── main.py              # 진입점 + 스케줄러
├── keep_client.py        # gkeepapi 래퍼
├── notion_wrapper.py     # Notion API 래퍼 (notion-client 패키지와 이름 충돌 방지를 위해 개명)
├── mapper.py              # Keep → Notion 데이터 변환
├── sync.py                # 동기화 로직 (중복 제거, 아카이브)
├── config.py              # 설정값 로드
├── create_database.py     # Notion DB 스키마 자동 생성 스크립트
├── get_master_token.py    # Google Master Token 최초 발급 스크립트
├── .env.example
├── requirements.txt
└── README.md
```

> 원 설계서는 Notion 래퍼 파일명을 `notion_client.py`로 지정했지만, 이는 설치된
> `notion-client` 패키지(`import notion_client`)와 이름이 겹쳐 스크립트 자신을
> 순환 참조(circular import)하며 즉시 실패합니다. 그래서 `notion_wrapper.py`로
> 이름을 바꿨습니다.

## 검증 방법

1. Keep에 테스트 메모 3개를 색상/라벨을 다르게 하여 작성합니다.
2. `python main.py`를 1회 실행합니다.
3. Notion DB에 3개 row가 생성되고 각 row의 `Keep_ID`가 채워져 있는지 확인합니다.
4. Keep에서 메모 1개를 삭제한 뒤 다시 실행 → 해당 row의 `상태`가 `아카이브`로 바뀌는지
   확인합니다.
5. 같은 메모로 다시 실행해도 row가 늘어나지 않는지 확인합니다 (Keep_ID 기준 중복 방지).
6. Notion DB 뷰를 갤러리 뷰로 전환해 포스트잇 형태로 보이는지 확인합니다.
