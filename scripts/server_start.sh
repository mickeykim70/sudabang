#!/bin/bash
# 수다방 서버 시작 (백엔드 + 프론트엔드)

PROJECT_DIR="$HOME/projects/sudabang"
LOG_DIR="$PROJECT_DIR/logs"
VENV_PYTHON="$PROJECT_DIR/backend/venv/bin/python3"

mkdir -p "$LOG_DIR"

# ── 백엔드 ──
if [ -f "$LOG_DIR/backend.pid" ] && kill -0 "$(cat "$LOG_DIR/backend.pid")" 2>/dev/null; then
    echo "백엔드 이미 실행 중 (PID: $(cat "$LOG_DIR/backend.pid"))"
else
    cd "$PROJECT_DIR/backend"
    nohup "$VENV_PYTHON" -m uvicorn main:app --host 0.0.0.0 --port 8000 \
        >> "$LOG_DIR/backend.log" 2>> "$LOG_DIR/backend.error.log" &
    echo $! > "$LOG_DIR/backend.pid"
    echo "백엔드 시작 (PID: $(cat "$LOG_DIR/backend.pid"))"
fi

# ── 프론트엔드 ──
if [ -f "$LOG_DIR/frontend.pid" ] && kill -0 "$(cat "$LOG_DIR/frontend.pid")" 2>/dev/null; then
    echo "프론트엔드 이미 실행 중 (PID: $(cat "$LOG_DIR/frontend.pid"))"
else
    cd "$PROJECT_DIR/frontend"
    nohup npm run dev -- --host 0.0.0.0 \
        >> "$LOG_DIR/frontend.log" 2>> "$LOG_DIR/frontend.error.log" &
    echo $! > "$LOG_DIR/frontend.pid"
    echo "프론트엔드 시작 (PID: $(cat "$LOG_DIR/frontend.pid"))"
fi

echo "완료. 확인: http://localhost:5173"
