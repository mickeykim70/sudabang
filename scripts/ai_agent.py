"""
AI 에이전트 — 두뇌(AIBrain) + 팔(AIWriter) 통합
"""
from ai_brain import AIBrain
from ai_writer import AIWriter
from config import BOARD_API_URL


class AIAgent:
    def __init__(self, username: str, password: str, display_name: str, api_key: str):
        """
        하나의 AI 에이전트 = 두뇌(AIBrain) + 팔(AIWriter)
        """
        self.brain = AIBrain(api_key=api_key)
        self.writer = AIWriter(base_url=BOARD_API_URL)
        self.display_name = display_name
        # 로그인
        self.writer.login(username, password)

    def post_article(self, board_id: int, topic: str, board_name: str) -> dict:
        """
        1. 두뇌가 글 생성
        2. 팔이 게시판에 등록
        """
        article = self.brain.write_article(topic, board_name)
        result = self.writer.write_post(
            board_id=board_id,
            title=article["title"],
            content=article["content"],
            source=article["source"],
        )
        return result

    def reply_to_post(self, post_id: int, board_name: str) -> dict:
        """
        1. 팔이 원글 읽기
        2. 두뇌가 댓글 생성
        3. 팔이 댓글 등록
        """
        post = self.writer.get_post(post_id)
        reply = self.brain.write_reply(post["content"], board_name)
        result = self.writer.write_comment(
            post_id=post_id,
            content=reply["content"],
        )
        return result

    def summarize_board(self, board_id: int, target_board_id: int, board_name: str) -> dict:
        """
        1. 팔이 게시판 글 목록 읽기
        2. 두뇌가 요약글 생성
        3. 팔이 다른 게시판에 요약글 등록
        """
        posts = self.writer.get_posts(board_id)
        summary = self.brain.summarize_thread(posts)
        result = self.writer.write_post(
            board_id=target_board_id,
            title=summary["title"],
            content=summary["content"],
            source=summary["source"],
        )
        return result
