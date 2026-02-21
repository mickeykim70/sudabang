"""
뉴스 포스트 이력 관리 — 중복 방지

구현:
- SQLite DB (data/news_tracker.db) 사용
- 테이블: posted_news (news_url TEXT UNIQUE, title TEXT, posted_at DATETIME)
- 뉴스 URL을 키로 중복 체크
- 기존 board.db와 별도 DB — 게시판 DB 건드리지 않음

메서드:
- is_posted(url) -> bool: 이미 포스트했는지 확인
- mark_posted(url, title): 포스트 완료 기록
- cleanup_old(days=30): 30일 이상 된 이력 삭제 (DB 비대화 방지)
"""
import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "news_tracker.db"
)


class NewsTracker:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posted_news (
                    news_url  TEXT PRIMARY KEY,
                    title     TEXT,
                    posted_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def is_posted(self, url: str) -> bool:
        """이미 포스트한 URL인지 확인"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT 1 FROM posted_news WHERE news_url = ?", (url,)
            ).fetchone()
        return row is not None

    def mark_posted(self, url: str, title: str):
        """포스트 완료로 기록 (중복 URL은 무시)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO posted_news (news_url, title) VALUES (?, ?)",
                (url, title),
            )
            conn.commit()

    def cleanup_old(self, days: int = 30):
        """오래된 이력 삭제 (DB 비대화 방지)"""
        cutoff = datetime.now() - timedelta(days=days)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "DELETE FROM posted_news WHERE posted_at < ?",
                (cutoff.isoformat(),),
            )
            conn.commit()
        return cur.rowcount
