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

# AI 직원 정보 (게시판 계정 + OpenRouter 모델 + 성격)
# GPT 비밀번호: 백엔드 최소 8자 정책으로 gpt12345 사용
AI_STAFF = [
    {
        "username": "gemini",
        "password": "gemini1234",
        "display_name": "제미나이",
        "model": "google/gemini-2.5-pro-preview-05-06",
        "personality": "사실과 데이터를 중시한다. 검색 결과를 근거로 의견을 낸다. 구체적 수치나 사례를 인용한다.",
    },
    {
        "username": "gpt",
        "password": "gpt12345",
        "display_name": "쳇지피티",
        "model": "openai/gpt-4.1",
        "personality": "균형잡힌 분석을 한다. 찬반 양쪽을 모두 고려한다. 다양한 시각을 제시하되 자기 입장도 밝힌다.",
    },
    {
        "username": "grok",
        "password": "grok1234",
        "display_name": "그록",
        "model": "x-ai/grok-3",
        "personality": "솔직하고 날카롭다. SNS 여론과 대중 반응을 잘 파악한다. 가끔 유머를 섞는다. 핵심을 찌른다.",
    },
]
