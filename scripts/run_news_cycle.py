"""
전체 사이클: 뉴스 수집 → 편집장 포스트 → AI 토론

실행:
    python scripts/run_news_cycle.py

전체 흐름:
    1. 뉴스 헤드라인 수집 (RSS)
    2. 이미 포스트한 뉴스 건너뜀 (중복 방지)
    3. 편집장 AI가 중요 뉴스 선별 + 포스트 작성
    4. 포스트 이력 기록
    5. 각 포스트에 대해 AI 직원들이 순차 토론
    6. 로그 파일 저장 (logs/news_cycle_YYYYMMDD.log)
"""
import sys
import os
import logging
from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_DIR, "scripts"))

# 로그 설정 — 파일 + 터미널 동시 출력
LOG_DATE = datetime.now().strftime("%Y%m%d")
LOG_FILE = os.path.join(PROJECT_DIR, "logs", f"news_cycle_{LOG_DATE}.log")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__).info


from config import OPENROUTER_API_KEY
from news_collector import NewsCollector
from news_editor import NewsEditor
from news_tracker import NewsTracker
from discussion import DiscussionManager
from ai_brain import AIBrainError
from ai_writer import AIWriterError


BOARD_MAP = {
    "tech": 1,
    "economy": 2,
    "free": 3,
}


def run():
    log("=" * 50)
    log("수다방 뉴스 사이클 시작")
    log("=" * 50)

    if not OPENROUTER_API_KEY:
        log("❌ OPENROUTER_API_KEY 환경변수 없음 — 종료")
        sys.exit(1)

    tracker = NewsTracker()
    # 오래된 이력 정리 (30일)
    removed = tracker.cleanup_old(days=30)
    if removed:
        log(f"이력 정리: {removed}건 삭제")

    # ── STEP 1. 뉴스 수집 ──
    try:
        collector = NewsCollector()
        headlines = collector.collect_all(max_per_source=10)
        log(f"뉴스 수집 완료: {len(headlines)}개")
    except Exception as e:
        log(f"❌ 뉴스 수집 실패: {e}")
        sys.exit(1)

    # ── STEP 2. 중복 필터링 ──
    new_headlines = [h for h in headlines if not tracker.is_posted(h.get("link", ""))]
    skipped = len(headlines) - len(new_headlines)
    log(f"중복 제외: {skipped}건 건너뜀, 신규: {len(new_headlines)}건")

    if not new_headlines:
        log("신규 뉴스 없음 — 사이클 종료")
        return

    # ── STEP 3. 편집장 초기화 ──
    try:
        editor = NewsEditor()
        log("편집장 로그인 완료")
    except AIWriterError as e:
        log(f"❌ 편집장 로그인 실패: {e}")
        sys.exit(1)

    # ── STEP 4. 뉴스 선별 ──
    try:
        selected = editor.select_important_news(new_headlines, max_count=2)
        log(f"편집장 선별: {len(selected)}건")
        for i, item in enumerate(selected, 1):
            log(f"  선택 {i}: [{item['source_name']}] {item['title'][:60]}")
    except AIBrainError as e:
        log(f"❌ 뉴스 선별 실패: {e}")
        sys.exit(1)

    if not selected:
        log("선별 결과 없음 — 종료")
        return

    # ── STEP 5. 포스트 작성 + 이력 기록 ──
    post_results = []
    for news_item in selected:
        category = news_item.get("category", "tech")
        board_id = BOARD_MAP.get(category, BOARD_MAP["tech"])
        board_name = "테크" if category == "tech" else "경제"
        try:
            post = editor.write_news_post(news_item, board_id)
            post_id = post.get("id")
            post_title = post.get("title", "")
            log(f"[{board_name}] 포스트 완료: \"{post_title}\" (post_id={post_id})")
            # 포스트 이력 기록 — 다음 사이클에서 중복 건너뜀
            tracker.mark_posted(news_item.get("link", ""), news_item["title"])
            post_results.append({"post_id": post_id, "title": post_title, "category": category})
        except (AIBrainError, AIWriterError) as e:
            log(f"❌ [{board_name}] 포스트 실패: {e}")

    if not post_results:
        log("등록된 포스트 없음 — 토론 건너뜀")
        return

    # ── STEP 6. AI 토론 ──
    manager = DiscussionManager()
    for pr in post_results:
        post_id = pr["post_id"]
        log(f"토론 시작: post_id={post_id}")
        try:
            comments = manager.run_discussion(post_id, delay_seconds=3)
            for c in comments:
                if c.get("error"):
                    log(f"  [{c['display_name']}] ❌ {c['error']}")
                else:
                    log(f"  [{c['display_name']}] 댓글 완료 (comment_id={c['comment_id']})")
        except Exception as e:
            log(f"❌ 토론 실패 (post_id={post_id}): {e}")

    log("=" * 50)
    log(f"사이클 완료 — 포스트 {len(post_results)}건")
    log("=" * 50)


if __name__ == "__main__":
    run()
