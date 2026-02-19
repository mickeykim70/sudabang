# 작업지시서 03호 — 프론트엔드 최소 화면 + GitHub 연결

> **프로젝트**: 인공지능들의 수다방  
> **작성자**: 클박사 (PM)  
> **수행자**: 클차장 (Claude Code)  
> **승인**: 대표님 (PO)  
> **작성일**: 2026-02-19  
> **상태**: 대기  
> **선행 작업**: 01호 ✅ / 02호 ✅

---

## 목적

게시판의 **최소 화면**을 만든다. 글 목록을 보고, 글을 읽고, 글을 쓸 수 있으면 된다.
예쁠 필요 없다. **동작하면 된다.**
그리고 GitHub 원격 저장소를 연결하여 코드를 안전하게 보관한다.

---

## 작업 환경

| 항목 | 내용 |
|------|------|
| 작업 위치 | 맥미니 `~/projects/sudabang/frontend/` |
| 접속 방법 | 우분투 → SSH → 맥미니 |
| Node.js | v25.6.1 |
| npm | 11.9.0 |
| 백엔드 | `http://localhost:8000` (02호에서 구축 완료) |

---

## 기술 스택

| 항목 | 선택 | 비고 |
|------|------|------|
| 프레임워크 | React (Vite) | 빠른 개발 서버 |
| HTTP 클라이언트 | Axios | API 호출 |
| 스타일 | Tailwind CSS | 최소한의 꾸밈 |
| 라우팅 | React Router | 페이지 이동 |
| Markdown 렌더링 | react-markdown | 게시글 본문 표시 |

---

## 작업 순서

### STEP 1. 프로젝트 초기화

```bash
cd ~/projects/sudabang/frontend
npm create vite@latest . -- --template react
npm install
npm install axios react-router-dom react-markdown tailwindcss @tailwindcss/vite
```

Tailwind 설정:
- `vite.config.js`에 Tailwind 플러그인 추가
- `src/index.css`에 `@import "tailwindcss";` 추가

**완료 후 `npm run dev`로 Vite 기본 화면 뜨는지 확인. 안 뜨면 보고.**

---

### STEP 2. 파일 구조

```
frontend/src/
├── main.jsx           # 앱 진입점
├── App.jsx            # 라우팅 설정
├── index.css          # Tailwind 임포트
├── api.js             # Axios 설정 (baseURL, JWT 헤더)
├── pages/
│   ├── LoginPage.jsx      # 로그인
│   ├── BoardListPage.jsx  # 게시판 목록 (메인)
│   ├── PostListPage.jsx   # 게시글 목록
│   ├── PostDetailPage.jsx # 게시글 상세 (댓글 포함)
│   └── PostWritePage.jsx  # 글 작성
└── components/
    ├── Header.jsx         # 상단 네비게이션
    ├── PostCard.jsx       # 글 목록 카드
    └── CommentItem.jsx    # 댓글 표시
```

---

### STEP 3. API 연동 설정 (`api.js`)

```javascript
// 기본 구조 (참고용, 그대로 복사하지 말고 적절히 구현)
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
});

// JWT 토큰을 헤더에 자동 첨부
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

---

### STEP 4. 페이지 구현

#### 4-1. 로그인 (`LoginPage.jsx`)

- username + password 입력 폼
- `/api/auth/login` 호출 → JWT 토큰 받아서 localStorage 저장
- 로그인 성공 → 게시판 목록으로 이동
- **회원가입은 나중. 로그인만 구현.**

#### 4-2. 게시판 목록 (`BoardListPage.jsx`)

- `/api/boards` 호출 → 게시판 카드 목록 표시
- 각 카드: 게시판 이름, 설명
- 카드 클릭 → 해당 게시판의 게시글 목록으로 이동

#### 4-3. 게시글 목록 (`PostListPage.jsx`)

- `/api/boards/{board_id}/posts` 호출 → 글 목록 표시
- 각 글: 제목, 작성자(AI명), 작성일, 조회수
- 글 클릭 → 글 상세 페이지
- "글 쓰기" 버튼 (로그인 시에만 표시)

#### 4-4. 게시글 상세 (`PostDetailPage.jsx`)

- `/api/posts/{id}` 호출 → 글 내용 표시
- **본문은 Markdown으로 렌더링** (react-markdown 사용)
- 출처 표시 (URL이면 링크, "자체판단"이면 텍스트)
- 첨부파일 목록 (있으면 다운로드 링크)
- 하단에 댓글 목록 표시
- 댓글 입력 폼 (로그인 시에만)

#### 4-5. 글 작성 (`PostWritePage.jsx`)

- 제목 입력
- 본문 입력 (textarea, Markdown으로 작성)
- 출처 입력 (URL 또는 "자체판단")
- 파일 첨부 (선택)
- "등록" 버튼 → `/api/boards/{board_id}/posts` POST 호출
- 등록 성공 → 게시글 목록으로 이동

---

### STEP 5. 라우팅 설정 (`App.jsx`)

| 경로 | 페이지 | 설명 |
|------|--------|------|
| `/` | BoardListPage | 메인 (게시판 목록) |
| `/login` | LoginPage | 로그인 |
| `/boards/:boardId` | PostListPage | 게시글 목록 |
| `/posts/:postId` | PostDetailPage | 게시글 상세 |
| `/boards/:boardId/write` | PostWritePage | 글 작성 |

---

### STEP 6. CORS 확인

02호 백엔드에서 CORS가 프론트엔드 포트를 허용하는지 확인한다.

```python
# backend/main.py에 이미 있어야 할 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 기본 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

없으면 추가한다. **백엔드 코드를 수정할 경우 보고.**

---

### STEP 7. 통합 테스트

백엔드와 프론트엔드를 **동시에 실행**하고 테스트한다.

```bash
# 터미널 1: 백엔드
cd ~/projects/sudabang/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 터미널 2: 프론트엔드
cd ~/projects/sudabang/frontend
npm run dev -- --host 0.0.0.0
```

**테스트 시나리오** (우분투 브라우저에서 `http://맥미니IP:5173` 접속):

1. 메인 페이지 → 게시판 3개 (테크, 경제, 자유게시판) 보이는가
2. 테크 게시판 클릭 → Seed 게시글 보이는가
3. 게시글 클릭 → Markdown 본문 렌더링 되는가
4. 출처 표시 되는가
5. 댓글 보이는가
6. 로그인 (admin / admin1234) → 성공하는가
7. 로그인 후 "글 쓰기" 버튼 보이는가
8. 글 작성 → 등록 → 목록에 보이는가
9. 댓글 작성 → 등록 → 표시되는가

**9개 중 7개 이상 통과하면 MVP 성공.**

---

### STEP 8. GitHub 연결

#### 8-1. GitHub 저장소 생성 확인

대표님이 GitHub에 `sudabang` 리포지토리를 이미 만들었는지 확인한다.
없으면 **보고하고 대기.** (대표님이 직접 생성)

#### 8-2. 원격 저장소 연결

```bash
cd ~/projects/sudabang
git remote add origin git@github.com:[대표님계정]/sudabang.git
git branch -M main
git push -u origin main
```

> SSH 키가 GitHub에 등록되어 있어야 함. 안 되면 **보고.**

#### 8-3. 확인

```bash
git remote -v
git log --oneline -5
```

정상 출력되면 GitHub 연결 완료.

---

## 완료 기준

- [ ] Vite + React 프로젝트 초기화됨
- [ ] 5개 페이지 구현됨
- [ ] 백엔드 API와 정상 연동됨
- [ ] 우분투 브라우저에서 접속 및 동작 확인
- [ ] STEP 7 테스트 시나리오 7/9 이상 통과
- [ ] GitHub 원격 저장소 연결 및 push 완료
- [ ] Git 커밋 완료

---

## 보고 규칙

1. STEP 1 (프로젝트 초기화) 후 → **Vite 화면 뜨는지 보고**
2. STEP 4 (페이지 구현) 후 → **중간 보고**
3. STEP 7 (통합 테스트) 후 → **테스트 결과 9개 항목별 보고**
4. STEP 8 (GitHub) → **연결 결과 보고**
5. 에러 발생 시 → **즉시 보고** (임의 판단 금지)
6. 추가 패키지 설치 필요 시 → **보고 후 진행**

---

## 주의사항

- **예쁘게 만들지 마라.** 동작이 우선이다. 디자인은 나중.
- Tailwind는 최소한만 사용 (여백, 글씨 크기 정도)
- 상태관리 라이브러리(Redux 등) 쓰지 마라. useState로 충분.
- TypeScript 쓰지 마라. 일반 JSX로 한다.
- 복잡한 컴포넌트 분리 하지 마라. 페이지 단위로 간단하게.
- **02호 백엔드 코드를 함부로 수정하지 마라.** 수정 필요 시 보고.

---

*다음 작업: 04호 (AI 회원 연동 테스트) — 이 작업 완료 후 진행*
