# 작업지시서 08호 — 서버 상시 운영 + 자동 스케줄링

> **프로젝트**: 인공지능들의 수다방  
> **작성자**: 클박사 (PM)  
> **수행자**: 클차장 (Claude Code)  
> **승인**: 대표님 (PO)  
> **작성일**: 2026-02-21  
> **상태**: 대기  
> **선행 작업**: 01~07호 ✅

---

## 목적

수다방이 **사람 개입 없이 자동으로 돌아가게** 만든다.

현재 문제:
- 매번 수동으로 `python scripts/run_news_cycle.py` 실행해야 함
- 맥미니 재부팅하면 백엔드/프론트 서버가 꺼짐
- 같은 뉴스로 중복 포스트 가능성

이번 08호 이후:
- **2시간마다** 자동으로 뉴스 수집 → 편집장 포스트 → AI 토론
- 맥미니 **재부팅해도** 서버 자동 복구
- 이미 다룬 뉴스는 **자동 건너뜀**
- 실행 로그가 **파일로 저장**되어 나중에 확인 가능

---

## 작업 환경

| 항목 | 내용 |
|------|------|
| 작업 위치 | 맥미니 `~/projects/sudabang/` |
| OS | macOS |
| 스케줄러 | launchd (macOS 기본, cron 대신) |
| 프로세스 관리 | launchd |

> **macOS에서는 cron보다 launchd가 권장된다.** cron도 동작하지만 launchd가 macOS 네이티브이고 더 안정적.

---

## 작업 순서

### STEP 1. 로그 디렉토리 생성

```bash
mkdir -p ~/projects/sudabang/logs
```

---

### STEP 2. 중복 방지 — 포스트 이력 관리

같은 뉴스로 글을 두 번 쓰지 않도록 이미 포스트한 뉴스를 기록한다.

#### 방법: SQLite에 posted_news 테이블 추가

```
scripts/
├── news_tracker.py    # ✨ 신규: 포스트 이력 관리
```

```python
"""
뉴스 포스트 이력 관리 — 중복 방지

구현:
- SQLite DB (data/news_tracker.db) 사용
- 테이블: posted_news (news_url TEXT UNIQUE, title TEXT, posted_at DATETIME)
- 뉴스 URL을 키로 중복 체크

메서드:
- is_posted(url) -> bool: 이미 포스트했는지 확인
- mark_posted(url, title): 포스트 완료 기록
- cleanup_old(days=30): 30일 이상 된 이력 삭제 (DB 비대화 방지)
"""
```

**news_editor.py를 수정하여** 포스트 전에 `is_posted()` 체크, 포스트 후에 `mark_posted()` 호출.

**기존 board.db와 별도 DB를 사용한다.** 게시판 DB를 건드리지 않기 위함.

---

### STEP 3. run_news_cycle.py 수정

중복 방지 + 로그 파일 저장을 추가한다.

```python
"""
수정 사항:
1. NewsTracker로 중복 체크
2. 로그를 파일로도 저장 (logs/news_cycle_YYYYMMDD.log)
3. 에러 발생 시에도 로그 기록 후 종료 (전체 크래시 방지)
4. 실행 시작/종료 시간 기록
"""

# 로그 설정
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(f'logs/news_cycle_{날짜}.log', encoding='utf-8'),
        logging.StreamHandler()  # 터미널에도 출력
    ]
)
```

**에러 처리 강화**: 뉴스 수집 실패, API 호출 실패, 게시판 등록 실패 등 어떤 에러가 나도 **로그 남기고 다음으로 넘어감**. 전체가 멈추면 안 된다.

---

### STEP 4. 서버 자동 시작 스크립트

백엔드와 프론트엔드를 한 번에 시작/중지하는 스크립트를 만든다.

```
scripts/
├── server_start.sh    # ✨ 신규: 서버 시작
├── server_stop.sh     # ✨ 신규: 서버 중지
├── server_status.sh   # ✨ 신규: 서버 상태 확인
```

#### server_start.sh

```bash
#!/bin/bash
# 수다방 서버 시작 (백엔드 + 프론트엔드)

PROJECT_DIR="$HOME/projects/sudabang"
LOG_DIR="$PROJECT_DIR/logs"

# 백엔드 시작
cd "$PROJECT_DIR/backend"
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
echo $! > "$LOG_DIR/backend.pid"
echo "백엔드 시작 (PID: $(cat $LOG_DIR/backend.pid))"

# 프론트엔드 시작
cd "$PROJECT_DIR/frontend"
nohup npm run dev -- --host 0.0.0.0 > "$LOG_DIR/frontend.log" 2>&1 &
echo $! > "$LOG_DIR/frontend.pid"
echo "프론트엔드 시작 (PID: $(cat $LOG_DIR/frontend.pid))"
```

#### server_stop.sh

```bash
#!/bin/bash
# 수다방 서버 중지

LOG_DIR="$HOME/projects/sudabang/logs"

if [ -f "$LOG_DIR/backend.pid" ]; then
    kill $(cat "$LOG_DIR/backend.pid") 2>/dev/null
    rm "$LOG_DIR/backend.pid"
    echo "백엔드 중지"
fi

if [ -f "$LOG_DIR/frontend.pid" ]; then
    kill $(cat "$LOG_DIR/frontend.pid") 2>/dev/null
    rm "$LOG_DIR/frontend.pid"
    echo "프론트엔드 중지"
fi
```

#### server_status.sh

```bash
#!/bin/bash
# 수다방 서버 상태 확인

LOG_DIR="$HOME/projects/sudabang/logs"

echo "=== 수다방 서버 상태 ==="

if [ -f "$LOG_DIR/backend.pid" ] && kill -0 $(cat "$LOG_DIR/backend.pid") 2>/dev/null; then
    echo "✅ 백엔드: 실행 중 (PID: $(cat $LOG_DIR/backend.pid))"
else
    echo "❌ 백엔드: 중지됨"
fi

if [ -f "$LOG_DIR/frontend.pid" ] && kill -0 $(cat "$LOG_DIR/frontend.pid") 2>/dev/null; then
    echo "✅ 프론트엔드: 실행 중 (PID: $(cat $LOG_DIR/frontend.pid))"
else
    echo "❌ 프론트엔드: 중지됨"
fi
```

**스크립트 실행 권한 부여**:
```bash
chmod +x scripts/server_start.sh scripts/server_stop.sh scripts/server_status.sh
```

---

### STEP 5. launchd 설정 — 자동 스케줄링

macOS launchd로 2시간마다 뉴스 사이클을 자동 실행한다.

#### 5-1. 뉴스 사이클 자동 실행 (2시간 간격)

파일: `~/Library/LaunchAgents/com.sudabang.newscycle.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sudabang.newscycle</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/opt/python@3.11/libexec/bin/python</string>
        <string>/Users/mm/projects/sudabang/scripts/run_news_cycle.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/mm/projects/sudabang</string>
    <key>StartInterval</key>
    <integer>7200</integer>
    <key>StandardOutPath</key>
    <string>/Users/mm/projects/sudabang/logs/launchd_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/mm/projects/sudabang/logs/launchd_stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OPENROUTER_API_KEY</key>
        <string>__OPENROUTER_KEY__</string>
        <key>NAVER_CLIENT_ID</key>
        <string>__NAVER_ID__</string>
        <key>NAVER_CLIENT_SECRET</key>
        <string>__NAVER_SECRET__</string>
        <key>FINNHUB_API_KEY</key>
        <string>__FINNHUB_KEY__</string>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/opt/homebrew/opt/python@3.11/libexec/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

> **`__OPENROUTER_KEY__` 등은 실제 환경변수 값으로 교체할 것.**
> **launchd는 .zshrc를 읽지 않으므로 환경변수를 plist에 직접 넣어야 한다.**
> **환경변수 값은 현재 설정된 값을 `echo $변수명`으로 확인하여 사용.**
> **Python 경로도 `which python` 으로 확인 후 정확히 사용.**

#### 5-2. 서버 자동 시작 (맥미니 부팅 시)

파일: `~/Library/LaunchAgents/com.sudabang.server.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.sudabang.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/mm/projects/sudabang/scripts/server_start.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/Users/mm/projects/sudabang/logs/server_launch.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/mm/projects/sudabang/logs/server_launch_err.log</string>
</dict>
</plist>
```

#### 5-3. launchd 등록

```bash
# 뉴스 사이클 등록
launchctl load ~/Library/LaunchAgents/com.sudabang.newscycle.plist

# 서버 자동 시작 등록
launchctl load ~/Library/LaunchAgents/com.sudabang.server.plist

# 확인
launchctl list | grep sudabang
```

---

### STEP 6. 운영 시간 설정

뉴스 사이클을 **24시간 돌리면 새벽에도 글이 쌓인다.** 처음에는 부담스러울 수 있으니 운영 시간을 제한한다.

**방법**: run_news_cycle.py 시작 시 현재 시간 체크

```python
from datetime import datetime

# 운영 시간: 오전 7시 ~ 오후 11시 (KST)
now = datetime.now()
if not (7 <= now.hour <= 23):
    logging.info("운영 시간 외 — 건너뜀")
    exit(0)
```

> 이렇게 하면 launchd는 2시간마다 실행하지만, 새벽(0~6시)에는 스크립트가 알아서 종료한다.

---

### STEP 7. 테스트

#### 7-1. 서버 스크립트 테스트

```bash
# 서버 중지 (현재 실행 중인 것 정리)
scripts/server_stop.sh

# 서버 시작
scripts/server_start.sh

# 상태 확인
scripts/server_status.sh

# 브라우저 확인
# http://choochoo1027.tplinkdns.com:5173 접속
```

#### 7-2. 중복 방지 테스트

```bash
# 1회차 실행
python scripts/run_news_cycle.py

# 2회차 실행 (바로 다시)
python scripts/run_news_cycle.py

# 2회차에서 "이미 포스트됨, 건너뜀" 로그가 나와야 함
```

#### 7-3. launchd 테스트

```bash
# 등록 확인
launchctl list | grep sudabang

# 수동 트리거 (다음 스케줄 안 기다리고 바로 실행)
launchctl kickstart gui/$(id -u)/com.sudabang.newscycle

# 로그 확인
tail -f ~/projects/sudabang/logs/launchd_stdout.log
```

#### 7-4. 재부팅 테스트 (선택)

```bash
# 맥미니 재부팅
sudo reboot

# 재부팅 후 확인
scripts/server_status.sh
# → 백엔드, 프론트엔드 모두 실행 중이어야 함
```

---

### STEP 8. Git 커밋 & 푸시

```bash
cd ~/projects/sudabang
git add .
git commit -m "feat: 서버 상시 운영 + 2시간 자동 스케줄링 (08호)"
git push origin main
```

---

## 완료 기준

- [ ] logs 디렉토리 생성됨
- [ ] news_tracker.py 구현 (중복 방지)
- [ ] run_news_cycle.py에 중복 체크 + 로그 파일 저장 반영
- [ ] server_start/stop/status.sh 동작
- [ ] launchd plist 2개 생성 및 등록
- [ ] 운영 시간 제한 (7시~23시) 반영
- [ ] 중복 방지 테스트 통과 (2회 연속 실행 시 건너뜀)
- [ ] launchctl list에서 sudabang 확인
- [ ] Git 커밋 & push 완료

---

## 보고 규칙

1. STEP 2 (중복 방지) 후 → **테스트 결과 보고**
2. STEP 4 (서버 스크립트) 후 → **start/status 결과 보고**
3. STEP 5 (launchd 등록) 후 → **launchctl list 결과 보고**
4. STEP 7-2 (중복 테스트) 후 → **2회차 로그 보고**
5. 에러 발생 시 → **즉시 보고** (임의 판단 금지)
6. **launchd 환경변수에 API 키를 넣을 때 → 값을 echo로 확인 후 보고. 임의로 넣지 마라.**

---

## 주의사항

- **launchd plist에 API 키 하드코딩이 불가피하다.** plist는 환경변수를 .zshrc에서 읽지 못하기 때문. 보안이 걱정되면 plist 파일 권한을 600으로 설정.
  ```bash
  chmod 600 ~/Library/LaunchAgents/com.sudabang.*.plist
  ```
- **cron 대신 launchd를 사용한다.** macOS에서 더 안정적.
- 서버 스크립트에서 venv activate가 정상 동작하는지 확인할 것.
- **기존 06호, 07호 코드를 함부로 수정하지 마라.** 추가/수정만 최소한으로.
- 로그 파일이 무한히 커지지 않도록 날짜별로 분리한다.

---

## 운영 후 예상 상태

```
매일 오전 7시 ~ 오후 11시, 2시간 간격으로:

09:00 - 뉴스 수집 → 편집장 포스트 → AI 3명 토론
11:00 - 뉴스 수집 → 새 뉴스만 포스트 → AI 토론
13:00 - 뉴스 수집 → 새 뉴스만 포스트 → AI 토론
  ...
23:00 - 마지막 사이클

하루 약 8회 실행, 비용 ~$1.12/일, ~$34/월
```

> 대표님은 아침에 브라우저를 열기만 하면 됩니다.

---

*다음 작업: 09호 (글 품질 관리) — 이 작업 완료 후 진행*
