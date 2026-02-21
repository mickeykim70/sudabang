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

# AI 직원별 모델 매핑 (OpenRouter 모델 ID)
AI_MODELS = {
    "claude": "anthropic/claude-sonnet-4.5",
    "gemini": "google/gemini-2.5-pro",
    "gpt": "openai/gpt-4.1",
    "grok": "x-ai/grok-3",
}

# 편집장 모델 (뉴스 선별용 — 비용 절약 위해 가벼운 모델)
EDITOR_MODEL = "anthropic/claude-sonnet-4.5"
