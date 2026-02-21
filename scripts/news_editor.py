"""
편집장 AI — 뉴스 선별 + 첫 포스트 작성

흐름:
1. 헤드라인 목록을 받는다
2. Claude(편집장)에게 "이 중 가장 중요한 뉴스 1~3개를 골라라" 요청
3. 선택된 뉴스에 대해 분석 게시글 작성
4. 게시판에 자동 등록
"""
from ai_brain import AIBrain, AIBrainError
from ai_writer import AIWriter, AIWriterError
from config import EDITOR_MODEL, BOARD_API_URL


class NewsEditor:
    def __init__(self):
        self.brain = AIBrain(model=EDITOR_MODEL)
        self.writer = AIWriter(base_url=BOARD_API_URL)
        # 편집장은 claude(클박사) 계정으로 로그인
        self.writer.login("claude", "claude1234")

    def select_important_news(self, headlines: list, max_count: int = 2) -> list:
        """
        헤드라인 목록에서 중요한 뉴스를 선별한다.

        반환값: [{"index": 0, "title": "...", "reason": "...", "category": "tech"}, ...]
        """
        if not headlines:
            return []

        selected = self.brain.select_news(headlines, max_count=max_count)

        # index로 원본 헤드라인 정보 병합
        result = []
        for item in selected:
            idx = item.get("index", 0)
            if 0 <= idx < len(headlines):
                merged = dict(headlines[idx])
                merged["reason"] = item.get("reason", "")
                # AI가 category를 재분류할 수 있으므로 덮어씀
                if item.get("category"):
                    merged["category"] = item["category"]
                result.append(merged)
        return result

    def write_news_post(self, news_item: dict, board_id: int) -> dict:
        """
        선택된 뉴스에 대해 분석 포스트를 작성하고 게시판에 등록한다.

        반환값: 등록된 포스트 정보 (post_id 포함)
        """
        article = self.brain.write_news_post(news_item)
        result = self.writer.write_post(
            board_id=board_id,
            title=article["title"],
            content=article["content"],
            source=article.get("source", news_item.get("link", "")),
        )
        return result

    def run(self, headlines: list, board_mapping: dict) -> list:
        """
        전체 편집 프로세스 실행

        board_mapping: {"tech": 1, "economy": 2, "free": 3}

        흐름:
        1. 중요 뉴스 선별
        2. 각 뉴스에 대해 포스트 작성
        3. 해당 카테고리 게시판에 등록
        4. 결과 리스트 반환
        """
        results = []

        # 1. 중요 뉴스 선별
        selected = self.select_important_news(headlines, max_count=2)

        # 2. 각 뉴스 포스트 작성 및 등록
        for news_item in selected:
            category = news_item.get("category", "tech")
            board_id = board_mapping.get(category, board_mapping.get("tech", 1))

            post = self.write_news_post(news_item, board_id)
            results.append({
                "news_title": news_item["title"],
                "post_id": post.get("id"),
                "post_title": post.get("title"),
                "board_id": board_id,
                "category": category,
            })

        return results
