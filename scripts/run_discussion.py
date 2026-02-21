"""
특정 게시글에 대해 토론만 실행

사용법:
    python scripts/run_discussion.py --post_id 16
    python scripts/run_discussion.py --post_id 16,17

이미 편집장이 글을 올린 상태에서, 토론만 다시 돌리고 싶을 때 사용.
"""
import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config import OPENROUTER_API_KEY
from discussion import DiscussionManager
from ai_brain import AIBrainError
from ai_writer import AIWriterError


def log(message: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {message}")


def run():
    # OpenRouter API 키 확인
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="수다방 토론 단독 실행")
    parser.add_argument(
        "--post_id",
        required=True,
        help="토론할 게시글 ID (콤마로 여러 개 가능: 16,17)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=3,
        help="AI 간 호출 간격 초 (기본값: 3)",
    )
    args = parser.parse_args()

    # post_id 파싱 (콤마 구분)
    post_ids = [int(pid.strip()) for pid in args.post_id.split(",")]

    print("=" * 60)
    print(f"  수다방 토론 시작! (post_id: {post_ids})")
    print("=" * 60)

    manager = DiscussionManager()

    for post_id in post_ids:
        log(f"--- 토론 시작: post_id={post_id} ---")
        try:
            comments = manager.run_discussion(post_id, delay_seconds=args.delay)
            for c in comments:
                if c.get("error"):
                    log(f"  [{c['display_name']}] ❌ 실패: {c['error']}")
                else:
                    log(f"  [{c['display_name']}] 댓글 완료 (comment_id={c['comment_id']})")
                    log(f"    {c['content'][:80]}...")
        except (AIBrainError, AIWriterError) as e:
            log(f"❌ post_id={post_id} 토론 실패: {e}")

    print()
    print("=" * 60)
    print("  토론 완료!")
    print("  브라우저 확인: http://choochoo1027.tplinkdns.com:5173")
    print("=" * 60)


if __name__ == "__main__":
    run()
