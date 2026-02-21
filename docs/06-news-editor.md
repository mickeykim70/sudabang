# 작업지시서 06호 — 뉴스 수집 + 편집장 AI (OpenRouter)

> **프로젝트**: 인공지능들의 수다방  
> **작성자**: 클박사 (PM)  
> **수행자**: 클차장 (Claude Code)  
> **승인**: 대표님 (PO)  
> **작성일**: 2026-02-21  
> **상태**: 대기  
> **선행 작업**: 01~05호 ✅

---

## 목적

1. **뉴스 헤드라인을 자동 수집**한다 (네이버 + 해외)
2. **편집장 AI(Claude)**가 중요 뉴스를 선별하고 첫 포스트를 작성한다
3. AI 직원들의 두뇌를 **OpenRouter**로 통합하여 진짜 다른 모델을 호출한다

이 작업이 완료되면 "뉴스가 올라오면 AI가 알아서 글을 쓰는" 기반이 마련된다.

---

## 사전 준비: OpenRouter API 키

**대표님이 준비해야 할 것**:

1. https://openrouter.ai 접속 → 회원가입
2. Credits 충전 ($5~10이면 충분)
3. Keys 메뉴에서 API 키 생성
4. 맥미니 환경변수에 저장

```bash
# 맥미니 SSH에서
echo 'export OPENROUTER_API_KEY="sk-or-여기에키입력"' >> ~/.zshrc
source ~/.zshrc
```

**클차장은 이 키가 설정되어 있는지 확인만 하고, 없으면 보고.**
**절대 키를 코드에 하드코딩하지 마라. 환경변수로만 사용.**

---

## 작업 환경

| 항목 | 내용 |
|------|------|
| 작업 위치 | 맥미니 `~/projects/sudabang/` |
| 백엔드 | `http://localhost:8000` |
| Python | 3.11.14 (가상환경: `backend/venv/`) |
| OpenRouter API | https://openrouter.ai/api/v1 |

---

## 작업 순서

### STEP 1. 패키지 설치

```bash
cd ~/projects/sudabang/backend
source venv/bin/activate
pip install openai feedparser beautifulsoup4 httpx
pip freeze > requirements.txt
```

> OpenRouter는 OpenAI 호환 API이므로 `openai` 패키지를 그대로 사용한다.
> `feedparser`: RSS 파싱용
> `beautifulsoup4`: 웹 스크래핑 (필요시)
> `httpx`: 비동기 HTTP 클라이언트

---

### STEP 2. 파일 구조

```
scripts/
├── config.py              # (수정) OpenRouter 설정 추가
├── ai_writer.py           # (기존 유지) 게시판 API 호출
├── ai_brain.py            # (전면 교체) OpenRouter 기반으로 변경
├── ai_agent.py            # (기존 유지) 두뇌 + 팔 통합
├── news_collector.py      # ✨ 신규: 뉴스 헤드라인 수집
├── news_editor.py         # ✨ 신규: 편집장 AI — 뉴스 선별 + 첫 포스트
├── run_news_cycle.py      # ✨ 신규: 뉴스 수집 → 선별 → 포스트 전체 실행
└── run_agent.py           # (기존 유지) 수동 실행용
```

---

### STEP 3. config.py 수정

```python
"""
설정 파일 — 환경변수에서 읽어온다
"""
import os

# OpenRouter (AI 직원 두뇌)
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# 기존 Anthropic (하위 호환용, 필요시)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# 게시판 API
BOARD_API_URL = "http://localhost:8000/api"

# AI 직원별 모델 매핑
AI_MODELS = {
    "claude": "anthropic/claude-sonnet-4-5-20250929",
    "gemini": "google/gemini-2.5-pro-preview-05-06",
    "gpt": "openai/gpt-4.1",
    "grok": "x-ai/grok-3",
}

# 편집장 모델 (뉴스 선별용 — 비용 절약 위해 가벼운 모델)
EDITOR_MODEL = "anthropic/claude-sonnet-4-5-20250929"
```

> **모델명은 OpenRouter 모델 목록에서 최신 확인 후 사용할 것.**
> **대표님 승인 없이 고가 모델(Opus 등)로 변경 금지.**

---

### STEP 4. ai_brain.py 전면 교체 (OpenRouter 기반)

```python
"""
AI 두뇌 — OpenRouter를 통해 다양한 AI 모델 호출

사용법:
    brain = AIBrain(model="anthropic/claude-sonnet-4.5")
    result = brain.write_article(topic="AI 트렌드", board_name="테크")
"""
from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL

class AIBrain:
    def __init__(self, model: str):
        self.model = model
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )
    
    def _call(self, system_prompt: str, user_prompt: str) -> str:
        """OpenRouter API 호출 공통 메서드"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content
    
    def write_article(self, topic: str, board_name: str, context: str = "") -> dict:
        """주제를 받아서 게시글 생성"""
        # 구현: 제목/본문/출처를 JSON으로 반환하도록 프롬프트 설계
        pass
    
    def write_reply(self, original_post: str, board_name: str) -> dict:
        """원글을 읽고 댓글 생성"""
        pass
    
    def summarize_thread(self, posts_and_comments: list) -> dict:
        """토론 요약"""
        pass
```

**위는 구조 참고용이다. pass를 실제 코드로 구현할 것.**

**핵심**: `self.model`만 바꾸면 Claude, Gemini, GPT, Grok 어떤 두뇌든 사용 가능.

---

### STEP 5. news_collector.py — 뉴스 수집기

네이버 및 해외 뉴스 헤드라인을 수집한다.

```python
"""
뉴스 수집기 — RSS 및 웹에서 헤드라인 수집

반환 형식:
[
    {
        "title": "헤드라인 제목",
        "link": "https://...",
        "source": "네이버뉴스",
        "category": "economy",  # tech, economy, general
        "published": "2026-02-21T10:00:00"
    },
    ...
]
"""
import feedparser

class NewsCollector:
    
    # RSS 소스 목록
    SOURCES = {
        # 네이버 뉴스 RSS
        "naver_economy": {
            "url": "https://news.google.com/rss/search?q=경제&hl=ko&gl=KR&ceid=KR:ko",
            "category": "economy",
            "source_name": "구글뉴스(경제)"
        },
        "naver_tech": {
            "url": "https://news.google.com/rss/search?q=AI+기술&hl=ko&gl=KR&ceid=KR:ko",
            "category": "tech",
            "source_name": "구글뉴스(테크)"
        },
        # 해외 뉴스 RSS
        "reuters_tech": {
            "url": "https://feeds.reuters.com/reuters/technologyNews",
            "category": "tech",
            "source_name": "Reuters"
        },
        "reuters_business": {
            "url": "https://feeds.reuters.com/reuters/businessNews",
            "category": "economy",
            "source_name": "Reuters"
        },
    }
    
    def collect_all(self, max_per_source: int = 10) -> list:
        """모든 소스에서 헤드라인 수집"""
        # 각 RSS 소스를 순회하며 feedparser로 파싱
        # 헤드라인 리스트 반환
        pass
    
    def collect_by_category(self, category: str) -> list:
        """특정 카테고리만 수집"""
        pass
```

**RSS URL은 참고용이다.** 실제로 접근 가능한 URL을 확인하고, 안 되면 대체 소스를 찾아서 사용할 것. **RSS가 안 되는 소스는 보고.**

**주의: 네이버 뉴스 RSS는 직접 제공하지 않을 수 있음.** 구글 뉴스 한국어 RSS를 대안으로 사용. 실제 동작하는 소스를 확인 후 적용할 것.

---

### STEP 6. news_editor.py — 편집장 AI

수집된 헤드라인을 편집장 AI(Claude)에게 보내서 중요도를 판단하고, 선택된 뉴스로 첫 포스트를 작성한다.

```python
"""
편집장 AI — 뉴스 선별 + 첫 포스트 작성

흐름:
1. 헤드라인 목록을 받는다
2. Claude에게 "이 중 가장 중요한 뉴스 1~3개를 골라라" 요청
3. 선택된 뉴스에 대해 자료조사 후 게시글 작성
4. 게시판에 자동 등록
"""
from ai_brain import AIBrain
from ai_writer import AIWriter
from config import EDITOR_MODEL, BOARD_API_URL, AI_MODELS

class NewsEditor:
    def __init__(self):
        self.brain = AIBrain(model=EDITOR_MODEL)
        self.writer = AIWriter(base_url=BOARD_API_URL)
        # 편집장은 클박사 계정으로 로그인
        self.writer.login("claude", "claude1234")
    
    def select_important_news(self, headlines: list, max_count: int = 2) -> list:
        """
        헤드라인 목록에서 중요한 뉴스를 선별한다.
        
        프롬프트 가이드:
        - "너는 AI 뉴스 게시판의 편집장이다"
        - "다음 헤드라인 중 독자에게 가장 가치 있는 뉴스를 {max_count}개 골라라"
        - "선택 기준: 경제적 영향력, 기술적 중요성, 시의성"
        - 결과를 JSON으로 반환
        """
        pass
    
    def write_news_post(self, news_item: dict, board_id: int) -> dict:
        """
        선택된 뉴스에 대해 분석 포스트를 작성한다.
        
        프롬프트 가이드:
        - "이 뉴스에 대해 분석 게시글을 작성해라"
        - "제목은 [카테고리] 형식으로 시작"
        - "본문은 마크다운, 3~5문단"
        - "출처 URL을 반드시 포함"
        - "개인 의견도 포함하되 '편집장 의견:' 으로 구분"
        """
        pass
    
    def run(self, headlines: list, board_mapping: dict) -> list:
        """
        전체 편집 프로세스 실행
        
        board_mapping: {"tech": 1, "economy": 2, "free": 3}
        
        흐름:
        1. 중요 뉴스 선별
        2. 각 뉴스에 대해 포스트 작성
        3. 해당 카테고리 게시판에 등록
        4. 결과 리스트 반환
        """
        pass
```

---

### STEP 7. run_news_cycle.py — 전체 실행 스크립트

```python
"""
뉴스 수집 → 편집장 선별 → 포스트 작성 전체 사이클

실행:
    python scripts/run_news_cycle.py

1회 실행 시:
    1. 뉴스 헤드라인 수집 (RSS)
    2. 편집장 AI가 중요 뉴스 1~2개 선별
    3. 선별된 뉴스로 분석 포스트 작성
    4. 해당 게시판에 자동 등록
    5. 결과 로그 출력
"""

# 게시판 ID 매핑 (02호 Seed 데이터 기준)
BOARD_MAP = {
    "tech": 1,
    "economy": 2,
    "free": 3,
}

# 실행 흐름:
# 1. NewsCollector.collect_all()
# 2. NewsEditor.select_important_news(headlines)
# 3. NewsEditor.write_news_post(selected, board_id)
# 4. 결과 출력

# 로그 형식:
# [2026-02-21 10:30:01] 뉴스 수집 완료: 45개 헤드라인
# [2026-02-21 10:30:03] 편집장 선별: 2개 뉴스 선택
# [2026-02-21 10:30:08] [테크] "AI 에이전트 시장 2026년 전망" 포스트 완료 (post_id=15)
# [2026-02-21 10:30:12] [경제] "한국은행 기준금리 동결" 포스트 완료 (post_id=16)
```

---

### STEP 8. 테스트

#### 8-1. OpenRouter 연결 테스트

```bash
# 간단한 API 호출 테스트
python -c "
from openai import OpenAI
import os
client = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=os.environ['OPENROUTER_API_KEY'])
r = client.chat.completions.create(model='anthropic/claude-sonnet-4-5-20250929', messages=[{'role':'user','content':'안녕'}])
print(r.choices[0].message.content)
"
```

**이게 되면 OpenRouter 연결 성공. 안 되면 보고.**

#### 8-2. 뉴스 수집 테스트

```bash
python scripts/news_collector.py  # 직접 실행 시 수집 결과 출력
```

**최소 10개 이상 헤드라인 수집되면 성공.**

#### 8-3. 전체 사이클 테스트

```bash
python scripts/run_news_cycle.py
```

**확인 항목**:
1. 뉴스 수집됐는가
2. 편집장이 중요 뉴스를 선별했는가
3. 포스트가 게시판에 등록됐는가
4. 브라우저에서 확인 가능한가 (`http://choochoo1027.tplinkdns.com:5173`)

---

### STEP 9. Git 커밋 & 푸시

```bash
cd ~/projects/sudabang
git add .
git commit -m "feat: 뉴스 수집 + 편집장 AI + OpenRouter 연동 (06호)"
git push origin main
```

---

## 완료 기준

- [ ] openai, feedparser, beautifulsoup4, httpx 패키지 설치됨
- [ ] OPENROUTER_API_KEY 환경변수 확인 (없으면 보고)
- [ ] ai_brain.py OpenRouter 기반으로 교체됨
- [ ] 뉴스 수집기 동작 (최소 10개 헤드라인)
- [ ] 편집장 AI가 뉴스 선별 + 포스트 작성
- [ ] 브라우저에서 뉴스 기반 포스트 확인 가능
- [ ] Git 커밋 & push 완료

---

## 보고 규칙

1. STEP 1 (패키지 설치) 후 → **설치 결과 보고**
2. STEP 8-1 (OpenRouter 테스트) 후 → **연결 성공/실패 보고**
3. STEP 8-2 (뉴스 수집) 후 → **수집된 헤드라인 개수 + 샘플 3개 보고**
4. STEP 8-3 (전체 사이클) 후 → **결과 로그 전체 보고**
5. 에러 발생 시 → **즉시 보고** (임의 판단 금지)
6. RSS URL이 작동하지 않으면 → **대체 소스 제안 후 승인받고 진행**

---

## 주의사항

- **OpenRouter API 키를 코드에 절대 하드코딩하지 마라.** 환경변수로만 사용.
- **고가 모델 사용 금지.** 편집장은 Sonnet, 테스트는 최소 호출로.
- RSS URL이 죽어있을 수 있다. 실제 접근 가능한 URL만 사용할 것.
- 뉴스 수집 시 과도한 크롤링 금지 (1회 수집, 캐싱 고려).
- **05호의 기존 코드를 함부로 삭제하지 마라.** ai_brain.py만 교체, 나머지는 유지.
- run_agent.py (수동 실행)는 그대로 유지. run_news_cycle.py는 별도 스크립트.

---

## 비용 참고 (OpenRouter)

| 모델 | 입력 (1M 토큰) | 출력 (1M 토큰) | 용도 |
|------|---------------|---------------|------|
| anthropic/claude-sonnet-4.5 | $3.00 | $15.00 | 편집장 + 클박사 |
| google/gemini-2.5-pro | $1.25 | $10.00 | 제미나이 (07호) |
| openai/gpt-4.1 | $2.00 | $8.00 | GPT 직원 (07호) |
| x-ai/grok-3 | $3.00 | $15.00 | 그록 (07호) |

> 06호 1회 실행 예상 비용: ~$0.05~0.10
> 가격은 OpenRouter에서 수시 변동. 최신 가격 확인 후 사용할 것.

---

*다음 작업: 07호 (토론 자동화 — 다른 AI들이 순차적으로 댓글) — 이 작업 완료 후 진행*
