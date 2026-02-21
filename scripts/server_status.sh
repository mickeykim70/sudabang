#!/bin/bash
# 수다방 서버 상태 확인

LOG_DIR="$HOME/projects/sudabang/logs"

echo "=== 수다방 서버 상태 ==="

if [ -f "$LOG_DIR/backend.pid" ] && kill -0 "$(cat "$LOG_DIR/backend.pid")" 2>/dev/null; then
    echo "✅ 백엔드:     실행 중 (PID: $(cat "$LOG_DIR/backend.pid")) — http://localhost:8000"
else
    echo "❌ 백엔드:     중지됨"
fi

if [ -f "$LOG_DIR/frontend.pid" ] && kill -0 "$(cat "$LOG_DIR/frontend.pid")" 2>/dev/null; then
    echo "✅ 프론트엔드: 실행 중 (PID: $(cat "$LOG_DIR/frontend.pid")) — http://localhost:5173"
else
    echo "❌ 프론트엔드: 중지됨"
fi

echo ""
echo "최근 백엔드 로그:"
tail -3 "$LOG_DIR/backend.log" 2>/dev/null || echo "  (로그 없음)"
