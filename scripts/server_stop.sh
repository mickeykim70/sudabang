#!/bin/bash
# 수다방 서버 중지

LOG_DIR="$HOME/projects/sudabang/logs"

if [ -f "$LOG_DIR/backend.pid" ]; then
    PID=$(cat "$LOG_DIR/backend.pid")
    if kill "$PID" 2>/dev/null; then
        echo "백엔드 중지 (PID: $PID)"
    else
        echo "백엔드 이미 중지됨"
    fi
    rm -f "$LOG_DIR/backend.pid"
else
    echo "백엔드 PID 파일 없음"
fi

if [ -f "$LOG_DIR/frontend.pid" ]; then
    PID=$(cat "$LOG_DIR/frontend.pid")
    if kill "$PID" 2>/dev/null; then
        echo "프론트엔드 중지 (PID: $PID)"
    else
        echo "프론트엔드 이미 중지됨"
    fi
    rm -f "$LOG_DIR/frontend.pid"
else
    echo "프론트엔드 PID 파일 없음"
fi
