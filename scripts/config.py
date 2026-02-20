"""
설정 파일 — 환경변수에서 읽어온다
"""
import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
BOARD_API_URL = "http://localhost:8000/api"
