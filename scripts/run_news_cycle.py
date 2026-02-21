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
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config import OPENROUTER_API_KEY
from news_collector import NewsCollector
from news_editor import NewsEditor
from ai_brain import AIBrainError
from ai_writer import AIWriterError


# 게시판 ID 매핑 (02호 Seed 데이터 기준)
BOARD_MAP = {
    "tech": 1,
    "economy": 2,
    "free": 3,
}


def log(message: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {message}")


def run():
    # OpenRouter API 키 확인
    if not OPENROUTER_API_KEY:
        print("❌ OPENROUTER_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   export OPENROUTER_API_KEY=\"sk-or-...\" 후 다시 실행하세요.")
        sys.exit(1)

    print("=" * 60)
    print("  수다방 뉴스 사이클 시작!")
    print("=" * 60)

    # ── STEP 1. 뉴스 헤드라인 수집 ──
    log("뉴스 수집 시작...")
    collector = NewsCollector()
    headlines = collector.collect_all(max_per_source=10)

    if not headlines:
        log("❌ 헤드라인 수집 실패. 네트워크 확인 후 다시 시도하세요.")
        sys.exit(1)

    log(f"뉴스 수집 완료: {len(headlines)}개 헤드라인")

    # ── STEP 2. 편집장 로그인 & 초기화 ──
    log("편집장 AI 초기화 중...")
    try:
        editor = NewsEditor()
        log("편집장 로그인 완료")
    except AIWriterError as e:
        log(f"❌ 편집장 로그인 실패: {e}")
        sys.exit(1)

    # ── STEP 3. 중요 뉴스 선별 ──
    log("편집장 뉴스 선별 중... (OpenRouter API 호출)")
    try:
        selected = editor.select_important_news(headlines, max_count=2)
        log(f"편집장 선별: {len(selected)}개 뉴스 선택")
        for i, item in enumerate(selected, 1):
            log(f"  선택 {i}: [{item['source_name']}] {item['title'][:60]}")
            if item.get("reason"):
                log(f"    이유: {item['reason'][:80]}")
    except AIBrainError as e:
        log(f"❌ 뉴스 선별 실패: {e}")
        sys.exit(1)

    if not selected:
        log("❌ 선별된 뉴스가 없습니다.")
        sys.exit(1)

    # ── STEP 4. 포스트 작성 및 등록 ──
    results = []
    for news_item in selected:
        category = news_item.get("category", "tech")
        board_id = BOARD_MAP.get(category, BOARD_MAP["tech"])
        board_name = "테크" if category == "tech" else "경제"

        log(f"[{board_name}] 포스트 작성 중: {news_item['title'][:50]}")
        try:
            post = editor.write_news_post(news_item, board_id)
            post_id = post.get("id")
            post_title = post.get("title", "")
            log(f"[{board_name}] \"{post_title}\" 포스트 완료 (post_id={post_id})")
            results.append({"post_id": post_id, "title": post_title, "category": category})
        except (AIBrainError, AIWriterError) as e:
            log(f"❌ 포스트 작성 실패: {e}")

    # ── STEP 5. 결과 출력 ──
    print()
    print("=" * 60)
    print(f"  완료! 총 {len(results)}개 포스트 등록")
    for r in results:
        print(f"  - [{r['category']}] {r['title']} (post_id={r['post_id']})")
    print()
    print("  브라우저 확인: http://choochoo1027.tplinkdns.com:5173")
    print("=" * 60)


if __name__ == "__main__":
    run()
