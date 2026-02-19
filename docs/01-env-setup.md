# 작업지시서 01호 — 맥미니 환경 확인 및 세팅

> **프로젝트**: 인공지능들의 수다방  
> **작성자**: 클박사 (PM)  
> **수행자**: 클차장 (Claude Code)  
> **승인**: 대표님 (PO)  
> **작성일**: 2026-02-19  
> **상태**: ✅ 완료 (2026-02-19)

---

## 작업 환경

| 항목 | 내용 |
|------|------|
| 작업 위치 | 맥미니 (모니터 없음, 서버 용도) |
| 접속 방법 | 우분투에서 SSH로 맥미니 접속 |
| 클코 위치 | 맥미니에 직접 설치되어 있음 |

**작업 흐름**:
```
우분투 터미널
  → ssh [맥미니]
    → cd ~/projects/sudabang
      → claude  (클코 실행)
        → "작업지시서 01호 읽고 STEP 1부터 진행해"
```

---

## 목적

게시판 서비스를 구축하기 위한 맥미니 개발 환경을 점검하고 세팅한다.
이 작업이 완료되어야 02호(백엔드 구축)를 진행할 수 있다.

---

## 작업 순서

### STEP 1. 현재 환경 점검 (보고 우선)

아래 항목을 확인하고 **결과를 보고**한다. 설치하지 말고 확인만 먼저.

```bash
# OS 및 하드웨어
sw_vers
uname -m
df -h  # 디스크 여유 공간

# 패키지 관리자
brew --version

# Python
python3 --version
pip3 --version
which python3

# Node.js
node --version
npm --version

# Git
git --version
git config user.name
git config user.email

# SQLite
sqlite3 --version

# 네트워크 (OpenClaw 연결 확인)
hostname
ifconfig | grep "inet "
```

**보고 형식**: 각 항목의 버전 또는 "미설치"를 표로 정리해서 보고할 것.

---

### STEP 2. 미설치 항목 설치

STEP 1 보고 후 대표님 승인을 받고 진행한다.

필요할 **가능성이 높은** 설치 목록 (STEP 1 결과에 따라 조정):

| 순서 | 항목 | 설치 명령어 | 용도 |
|------|------|-------------|------|
| 1 | Homebrew | `/bin/bash -c "$(curl -fsSL ...)"` | 패키지 관리자 |
| 2 | Python 3.11+ | `brew install python@3.11` | 백엔드 (FastAPI) |
| 3 | Node.js 20 LTS | `brew install node@20` | 프론트엔드 (React) |
| 4 | Git | `brew install git` | 버전 관리 |
| 5 | SQLite | macOS 기본 내장 (확인만) | 데이터베이스 |

**주의사항**:
- 이미 설치된 것은 건드리지 않는다
- 버전이 너무 낮은 경우에만 업그레이드 (Python 3.9 미만, Node 16 미만)
- 설치 중 에러 발생 시 **멈추고 보고**한다

---

### STEP 3. 프로젝트 폴더 구조 생성

```
~/projects/sudabang/
├── README.md                # 프로젝트 설명
├── docs/
│   ├── project-goal.md      # 목표 문서 (클박사 관리)
│   └── work/
│       ├── 01-env-setup.md  # 이 작업지시서
│       ├── 02-backend.md    # (예정)
│       ├── 03-frontend.md   # (예정)
│       └── 04-ai-connect.md # (예정)
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   └── ...
├── frontend/
│   ├── package.json
│   └── ...
├── data/
│   └── board.db             # SQLite DB 파일 (STEP 4에서 생성)
└── uploads/                  # 첨부파일 저장소
```

**실행할 것**:
```bash
mkdir -p ~/projects/sudabang/{docs/work,backend,frontend,data,uploads}
touch ~/projects/sudabang/README.md
```

---

### STEP 4. Python 가상환경 + 기본 패키지

```bash
cd ~/projects/sudabang/backend
python3 -m venv venv
source venv/bin/activate

pip install fastapi uvicorn sqlalchemy aiosqlite pydantic python-jose[cryptography] passlib[bcrypt] python-multipart
pip freeze > requirements.txt
```

---

### STEP 5. SQLite DB 초기화 확인

DB 파일 생성만 확인한다. 스키마는 02호에서 작업.

```bash
cd ~/projects/sudabang/data
sqlite3 board.db "SELECT sqlite_version();"
```

정상 출력되면 DB 준비 완료.

---

### STEP 6. Git 초기화

```bash
cd ~/projects/sudabang
git init
```

`.gitignore` 생성:
```
# Python
backend/venv/
__pycache__/
*.pyc

# Node
frontend/node_modules/

# DB
data/board.db

# OS
.DS_Store

# 첨부파일 (용량 큼)
uploads/*
!uploads/.gitkeep
```

```bash
git add .
git commit -m "init: 프로젝트 구조 생성 및 환경 세팅"
```

---

## 완료 기준

- [x] STEP 1 환경 점검 결과 보고 완료
- [x] 필요한 도구 모두 설치됨 (Python 3.11.14)
- [x] 프로젝트 폴더 구조 생성됨
- [x] Python 가상환경 + 패키지 설치됨
- [x] SQLite 정상 동작 확인
- [x] Git 초기 커밋 완료

---

## 보고 규칙

1. STEP 1 완료 후 → **결과 보고** (설치 진행 전)
2. 전체 완료 후 → **완료 보고**
3. 에러 발생 시 → **즉시 보고** (임의 판단 금지)

---

*다음 작업: 02호 (게시판 백엔드 API) — 이 작업 완료 후 진행*
