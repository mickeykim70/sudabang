"""
뉴스 수집기 — RSS에서 헤드라인 수집

반환 형식:
[
    {
        "title": "헤드라인 제목",
        "link": "https://...",
        "source_name": "구글뉴스(경제)",
        "category": "economy",  # tech, economy
        "published": "2026-02-21T10:00:00"
    },
    ...
]

직접 실행 시 수집 결과를 출력한다:
    python scripts/news_collector.py
"""
import feedparser
from datetime import datetime


class NewsCollector:

    # RSS 소스 목록 (실제 접근 가능한 소스만 사용)
    SOURCES = {
        "google_tech_kr": {
            "url": "https://news.google.com/rss/search?q=AI+기술&hl=ko&gl=KR&ceid=KR:ko",
            "category": "tech",
            "source_name": "구글뉴스(테크)",
        },
        "google_economy_kr": {
            "url": "https://news.google.com/rss/search?q=경제&hl=ko&gl=KR&ceid=KR:ko",
            "category": "economy",
            "source_name": "구글뉴스(경제)",
        },
        "google_ai_en": {
            "url": "https://news.google.com/rss/search?q=AI+technology&hl=en&gl=US&ceid=US:en",
            "category": "tech",
            "source_name": "Google News(AI)",
        },
        "hacker_news": {
            "url": "https://news.ycombinator.com/rss",
            "category": "tech",
            "source_name": "Hacker News",
        },
    }

    def _parse_entry(self, entry: dict, source_meta: dict) -> dict:
        """RSS 엔트리를 통일된 형식으로 변환"""
        # 발행 시간 파싱
        published = ""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published = datetime(*entry.published_parsed[:6]).isoformat()
            except Exception:
                published = ""

        return {
            "title": entry.get("title", "").strip(),
            "link": entry.get("link", ""),
            "source_name": source_meta["source_name"],
            "category": source_meta["category"],
            "published": published,
        }

    def collect_all(self, max_per_source: int = 10) -> list:
        """모든 소스에서 헤드라인 수집"""
        results = []
        for source_key, meta in self.SOURCES.items():
            try:
                feed = feedparser.parse(meta["url"])
                entries = feed.entries[:max_per_source]
                for entry in entries:
                    item = self._parse_entry(entry, meta)
                    if item["title"]:  # 제목 없는 항목 제외
                        results.append(item)
                print(f"  [{meta['source_name']}] {len(entries)}개 수집")
            except Exception as e:
                print(f"  [{meta['source_name']}] 수집 실패: {e}")
        return results

    def collect_by_category(self, category: str) -> list:
        """특정 카테고리만 수집"""
        results = []
        for source_key, meta in self.SOURCES.items():
            if meta["category"] != category:
                continue
            try:
                feed = feedparser.parse(meta["url"])
                for entry in feed.entries[:10]:
                    item = self._parse_entry(entry, meta)
                    if item["title"]:
                        results.append(item)
            except Exception as e:
                print(f"  [{meta['source_name']}] 수집 실패: {e}")
        return results


if __name__ == "__main__":
    print("뉴스 헤드라인 수집 중...")
    collector = NewsCollector()
    headlines = collector.collect_all(max_per_source=10)

    print(f"\n총 {len(headlines)}개 헤드라인 수집 완료\n")
    print("=" * 60)

    # 카테고리별 출력
    for category in ["tech", "economy"]:
        items = [h for h in headlines if h["category"] == category]
        print(f"\n[{category.upper()}] {len(items)}개")
        for i, item in enumerate(items[:5], 1):
            print(f"  {i}. [{item['source_name']}] {item['title'][:60]}")
