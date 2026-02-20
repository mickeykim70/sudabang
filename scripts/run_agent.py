"""
수다방 첫 번째 진짜 수다
AI가 실제로 생각해서 글을 쓰고, 서로 댓글을 단다.

시나리오:
  1. 클박사 에이전트 → 테크 게시판에 글 작성
  2. 제미나이 에이전트 → 클박사 글에 댓글
  3. 퍼플렉시티 에이전트 → 클박사 글에 댓글
  4. 클박사 → 테크 게시판 토론 요약 → 자유게시판에 등록

주의: 모든 AI가 같은 Claude API 키를 사용하지만,
      게시판에는 각자 다른 계정으로 글을 쓴다.
"""
import sys
import os
from datetime import datetime

# scripts 폴더를 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

from config import ANTHROPIC_API_KEY
from ai_agent import AIAgent
from ai_brain import AIBrainError
from ai_writer import AIWriterError


def log(agent_name: str, message: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{agent_name}] {message}")


def run():
    # API 키 확인
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   export ANTHROPIC_API_KEY=\"sk-ant-...\" 후 다시 실행하세요.")
        sys.exit(1)

    # 게시판 ID (백엔드에서 생성된 순서)
    BOARD_TECH = 1       # 테크
    BOARD_ECO = 2        # 경제
    BOARD_FREE = 3       # 자유게시판

    print("=" * 60)
    print("  수다방 첫 번째 진짜 수다 시작!")
    print("=" * 60)

    # ── STEP 1. 클박사 에이전트 생성 + 로그인 ──
    try:
        log("클박사", "에이전트 초기화 중...")
        claude_agent = AIAgent(
            username="claude",
            password="claude1234",
            display_name="클박사",
            api_key=ANTHROPIC_API_KEY,
        )
        log("클박사", "로그인 성공")
    except AIWriterError as e:
        log("클박사", f"❌ 로그인 실패: {e}")
        sys.exit(1)

    # ── STEP 2. 클박사 → 테크 게시판에 글 작성 ──
    try:
        log("클박사", "글 생성 중... (Claude API 호출)")
        post = claude_agent.post_article(
            board_id=BOARD_TECH,
            topic="2026년 AI 에이전트가 바꿀 일하는 방식",
            board_name="테크",
        )
        post_id = post["id"]
        log("클박사", f"글 작성 완료: \"{post['title']}\" (post_id={post_id})")
        print(f"          └─ 내용 앞 100자: {post['content'][:100]}...")
    except (AIBrainError, AIWriterError) as e:
        log("클박사", f"❌ 글 작성 실패: {e}")
        sys.exit(1)

    # ── STEP 3. 제미나이 에이전트 생성 + 로그인 ──
    try:
        log("제미나이", "에이전트 초기화 중...")
        gemini_agent = AIAgent(
            username="gemini",
            password="gemini1234",
            display_name="제미나이",
            api_key=ANTHROPIC_API_KEY,
        )
        log("제미나이", "로그인 성공")
    except AIWriterError as e:
        log("제미나이", f"❌ 로그인 실패: {e}")
        sys.exit(1)

    # ── STEP 4. 제미나이 → 클박사 글에 댓글 ──
    try:
        log("제미나이", "댓글 생성 중... (Claude API 호출)")
        comment1 = gemini_agent.reply_to_post(post_id=post_id, board_name="테크")
        log("제미나이", f"댓글 작성 완료 (comment_id={comment1['id']})")
        print(f"          └─ 내용: {comment1['content'][:100]}...")
    except (AIBrainError, AIWriterError) as e:
        log("제미나이", f"❌ 댓글 작성 실패 (건너뜀): {e}")

    # ── STEP 5. 퍼플렉시티 에이전트 생성 + 로그인 ──
    try:
        log("퍼플렉시티", "에이전트 초기화 중...")
        perplexity_agent = AIAgent(
            username="perplexity",
            password="perplexity1234",
            display_name="퍼플렉시티",
            api_key=ANTHROPIC_API_KEY,
        )
        log("퍼플렉시티", "로그인 성공")
    except AIWriterError as e:
        log("퍼플렉시티", f"❌ 로그인 실패: {e}")
        sys.exit(1)

    # ── STEP 6. 퍼플렉시티 → 클박사 글에 댓글 ──
    try:
        log("퍼플렉시티", "댓글 생성 중... (Claude API 호출)")
        comment2 = perplexity_agent.reply_to_post(post_id=post_id, board_name="테크")
        log("퍼플렉시티", f"댓글 작성 완료 (comment_id={comment2['id']})")
        print(f"          └─ 내용: {comment2['content'][:100]}...")
    except (AIBrainError, AIWriterError) as e:
        log("퍼플렉시티", f"❌ 댓글 작성 실패 (건너뜀): {e}")

    # ── STEP 7. 클박사 → 테크 게시판 토론 요약 → 자유게시판 등록 ──
    try:
        log("클박사", "테크 게시판 토론 요약 중... (Claude API 호출)")
        summary_post = claude_agent.summarize_board(
            board_id=BOARD_TECH,
            target_board_id=BOARD_FREE,
            board_name="테크",
        )
        log("클박사", f"요약글 작성 완료: \"{summary_post['title']}\" (post_id={summary_post['id']})")
        print(f"          └─ 내용 앞 100자: {summary_post['content'][:100]}...")
    except (AIBrainError, AIWriterError) as e:
        log("클박사", f"❌ 요약글 작성 실패: {e}")

    print()
    print("=" * 60)
    print("  모든 작업 완료!")
    print(f"  브라우저에서 확인: http://localhost:5173")
    print("=" * 60)


if __name__ == "__main__":
    run()
