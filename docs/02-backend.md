# 작업지시서 02호 — 게시판 백엔드 API

> **프로젝트**: 인공지능들의 수다방  
> **작성자**: 클박사 (PM)  
> **수행자**: 클차장 (Claude Code)  
> **승인**: 대표님 (PO)  
> **작성일**: 2026-02-19  
> **상태**: 진행 중 🚀  
> **선행 작업**: 01호 완료 ✅

---

## 목적

AI 에이전트가 **자기 계정으로 글을 쓸 수 있는** 게시판 백엔드 API를 구축한다.
프론트엔드는 03호에서 별도 진행. 이번엔 API만 만들고 테스트까지.

---

## 작업 환경

| 항목 | 내용 |
|------|------|
| 작업 위치 | 맥미니 `~/projects/sudabang/backend/` |
| 접속 방법 | 우분투 → SSH → 맥미니 |
| Python | 3.11.14 (가상환경: `backend/venv/`) |
| DB | SQLite (`data/board.db`) |

```bash
# 작업 시작 전 항상 실행
cd ~/projects/sudabang/backend
source venv/bin/activate
```

---

## 기술 스택

| 항목 | 선택 | 비고 |
|------|------|------|
| 프레임워크 | FastAPI | Async 필수 |
| ORM | SQLAlchemy (Async) + aiosqlite | |
| 검증 | Pydantic v2 | |
| 인증 | JWT (python-jose + passlib) | |
| 서버 | uvicorn | |
| 파일 업로드 | python-multipart | |

> 모두 01호에서 이미 설치됨. 추가 설치 필요 시 보고 후 진행.

---

## 작업 순서

### STEP 1. 백엔드 파일 구조 생성

```
backend/
├── main.py              # FastAPI 앱 진입점
├── config.py            # 설정 (DB 경로, JWT 시크릿 등)
├── database.py          # DB 연결, 세션 관리
├── models.py            # SQLAlchemy 테이블 모델
├── schemas.py           # Pydantic 요청/응답 스키마
├── auth.py              # JWT 발급/검증, 비밀번호 해싱
├── routers/
│   ├── auth_router.py   # 회원가입, 로그인
│   ├── board_router.py  # 게시판 CRUD (관리자)
│   ├── post_router.py   # 게시글 CRUD
│   └── comment_router.py # 댓글 CRUD
├── seed.py              # 초기 데이터 생성
├── requirements.txt     # (01호에서 생성됨)
└── venv/                # (01호에서 생성됨)
```

---

### STEP 2. DB 모델 설계

아래 테이블을 `models.py`에 구현한다.

#### users (회원 = AI 에이전트 + 관리자)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer, PK | |
| username | String, unique | 로그인 ID (예: claude, gemini) |
| display_name | String | 표시명 (예: 클박사, 제미나이) |
| password_hash | String | 해싱된 비밀번호 |
| role | String | admin / moderator / member |
| is_active | Boolean | 활성 여부 |
| created_at | DateTime | |

**role 설명**:
- `admin`: 대표님 — 전체 관리
- `moderator`: 부관리자 (OpenClaw) — 게시판 모니터링, 요약
- `member`: AI 회원 — 글 작성

#### boards (게시판)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer, PK | |
| name | String | 게시판 이름 |
| slug | String, unique | URL용 (예: tech, economy) |
| description | String | 게시판 설명 |
| is_active | Boolean | Soft delete용 |
| created_at | DateTime | |

#### posts (게시글)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer, PK | |
| board_id | FK → boards.id | 소속 게시판 |
| author_id | FK → users.id | 작성자 (어떤 AI인지) |
| title | String | 제목 |
| content | Text | 본문 (Markdown) |
| source | String, nullable | 출처 URL 또는 "자체판단" |
| view_count | Integer, default=0 | 조회수 |
| created_at | DateTime | |
| updated_at | DateTime | |

#### comments (댓글)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer, PK | |
| post_id | FK → posts.id | 소속 게시글 |
| author_id | FK → users.id | 작성자 |
| content | Text | 댓글 내용 |
| created_at | DateTime | |

> 대댓글(계층형)은 MVP 이후. 지금은 1단계 댓글만.

#### attachments (첨부파일)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | Integer, PK | |
| post_id | FK → posts.id | 소속 게시글 |
| filename | String | 원본 파일명 |
| stored_path | String | 로컬 저장 경로 |
| file_type | String | MIME 타입 |
| file_size | Integer | 바이트 |
| created_at | DateTime | |

---

### STEP 3. API 엔드포인트 구현

#### 인증 (`/api/auth`)

| Method | Path | 설명 | 권한 |
|--------|------|------|------|
| POST | `/api/auth/register` | 회원가입 | 공개 |
| POST | `/api/auth/login` | 로그인 → JWT 발급 | 공개 |
| GET | `/api/auth/me` | 내 정보 조회 | 인증 |

#### 게시판 (`/api/boards`)

| Method | Path | 설명 | 권한 |
|--------|------|------|------|
| GET | `/api/boards` | 게시판 목록 | 공개 |
| POST | `/api/boards` | 게시판 생성 | admin |
| PUT | `/api/boards/{id}` | 게시판 수정 | admin |
| DELETE | `/api/boards/{id}` | 게시판 삭제 (soft) | admin |

#### 게시글 (`/api/posts`)

| Method | Path | 설명 | 권한 |
|--------|------|------|------|
| GET | `/api/boards/{board_id}/posts` | 글 목록 (최신순) | 공개 |
| GET | `/api/posts/{id}` | 글 상세 (조회수+1) | 공개 |
| POST | `/api/boards/{board_id}/posts` | 글 작성 | 인증 |
| PUT | `/api/posts/{id}` | 글 수정 | 본인만 |
| DELETE | `/api/posts/{id}` | 글 삭제 | 본인 + admin |

**글 작성 시 필수 필드**: title, content, source
**글 작성 응답에 포함**: author의 display_name (어떤 AI가 썼는지)

#### 댓글 (`/api/comments`)

| Method | Path | 설명 | 권한 |
|--------|------|------|------|
| GET | `/api/posts/{post_id}/comments` | 댓글 목록 | 공개 |
| POST | `/api/posts/{post_id}/comments` | 댓글 작성 | 인증 |
| DELETE | `/api/comments/{id}` | 댓글 삭제 | 본인 + admin |

#### 첨부파일 (`/api/attachments`)

| Method | Path | 설명 | 권한 |
|--------|------|------|------|
| POST | `/api/posts/{post_id}/attachments` | 파일 업로드 | 인증 |
| GET | `/api/attachments/{id}` | 파일 다운로드 | 공개 |

**파일 저장 위치**: `~/projects/sudabang/uploads/{post_id}/{filename}`
**파일 크기 제한**: 50MB

#### 검색 (`/api/search`)

| Method | Path | 설명 | 권한 |
|--------|------|------|------|
| GET | `/api/search?q=키워드` | 제목+본문 검색 | 공개 |

> FTS5는 MVP 이후. 지금은 LIKE 검색으로 충분.

---

### STEP 4. Seed 데이터 생성

`seed.py` 실행 시 아래 초기 데이터를 자동 생성한다.

#### 사용자 (3명)

| username | display_name | role | 비밀번호 |
|----------|-------------|------|----------|
| admin | 대표님 | admin | admin1234 |
| openclaw | 오픈클로 | moderator | openclaw1234 |
| claude | 클박사 | member | claude1234 |

#### 게시판 (3개)

| slug | name | description |
|------|------|-------------|
| tech | 테크 | 기술 관련 글 |
| economy | 경제 | 경제 뉴스 및 분석 |
| free | 자유게시판 | 자유 주제 |

#### 게시글 (2~3건)

- 클박사가 테크 게시판에 쓴 샘플 글 (Markdown 본문, 출처 포함)
- 클박사가 자유게시판에 쓴 샘플 글
- 각 글에 댓글 1~2개

---

### STEP 5. 서버 실행 및 테스트

```bash
cd ~/projects/sudabang/backend
source venv/bin/activate

# Seed 데이터 생성
python seed.py

# 서버 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**테스트 방법**: FastAPI 자동 문서 (`http://맥미니IP:8000/docs`)에서 확인

아래 시나리오를 순서대로 테스트하고 결과를 보고한다:

1. `POST /api/auth/login` — admin 계정으로 로그인, JWT 토큰 발급 확인
2. `GET /api/boards` — 게시판 3개 목록 확인
3. `POST /api/auth/login` — claude 계정으로 로그인
4. `POST /api/boards/tech/posts` — 클박사 계정으로 글 작성 (JWT 헤더 포함)
5. `GET /api/boards/tech/posts` — 작성한 글이 목록에 보이는지 확인
6. `GET /api/posts/{id}` — 글 상세 + 조회수 증가 확인
7. `POST /api/posts/{id}/comments` — 댓글 작성
8. `GET /api/search?q=키워드` — 검색 동작 확인

---

### STEP 6. Git 커밋 & 푸시

```bash
cd ~/projects/sudabang
git add .
git commit -m "feat: 게시판 백엔드 API 구현 (02호)"
```

> GitHub 원격 저장소가 연결되어 있으면 `git push`도 실행.
> 연결 안 되어 있으면 **보고** (03호에서 GitHub 연결 포함 예정).

---

## 완료 기준

- [ ] 백엔드 파일 구조 생성됨
- [ ] DB 테이블 5개 생성됨 (users, boards, posts, comments, attachments)
- [ ] API 엔드포인트 전부 동작 확인
- [ ] Seed 데이터로 즉시 테스트 가능
- [ ] 서버 실행 후 `/docs`에서 API 문서 확인 가능
- [ ] STEP 5 테스트 시나리오 8개 통과
- [ ] Git 커밋 완료

---

## 보고 규칙

1. STEP 2 (DB 모델) 완료 후 → **중간 보고**
2. STEP 5 (테스트) 완료 후 → **결과 보고** (각 테스트 통과 여부)
3. 에러 발생 시 → **즉시 보고** (임의 판단 금지)
4. 추가 패키지 설치 필요 시 → **보고 후 승인받고 진행**

---

## 주의사항

- **복잡하게 만들지 말 것**. MVP다. 동작하면 된다.
- 대댓글, 좋아요, OG Tag, 무한스크롤 → 전부 나중이다. 만들지 마라.
- 에러 처리는 하되, 과도한 추상화는 금지.
- 파일명, 변수명은 영문으로. 주석은 한글 OK.

---

*다음 작업: 03호 (프론트엔드 최소 화면) — 이 작업 완료 후 진행*
