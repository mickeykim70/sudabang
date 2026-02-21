"""
토론 스케줄러 — AI 직원들이 순차적으로 편집장 글에 댓글을 단다

흐름:
1. 편집장이 작성한 글(post_id)을 받는다
2. AI 직원 목록을 순회한다
3. 각 AI가:
   a. 자기 모델(두뇌)로 원글 + 이전 댓글들을 읽고 의견 생성
   b. 자기 게시판 계정(팔)으로 댓글 등록
4. 다음 AI로 넘어간다 (delay_seconds 간격)
5. 모든 AI가 댓글을 달면 종료

핵심:
    이전 AI의 댓글을 다음 AI에게 전달 → 토론이 "쌓인다"

    원글 (편집장)
      → 제미나이: 원글만 보고 의견
      → GPT: 원글 + 제미나이 댓글 보고 의견
      → 그록: 원글 + 제미나이 + GPT 댓글 보고 의견
"""
import time
from ai_brain import AIBrain, AIBrainError
from ai_writer import AIWriter, AIWriterError
from config import AI_STAFF, BOARD_API_URL


class DiscussionManager:

    def __init__(self):
        self.staff = AI_STAFF
        # 게시글 읽기용 (비로그인으로도 가능하지만 writer 재활용)
        self._reader = AIWriter(base_url=BOARD_API_URL)

    def run_discussion(self, post_id: int, delay_seconds: int = 5) -> list:
        """
        하나의 게시글에 대해 AI 직원들이 순차적으로 토론한다.

        Args:
            post_id: 편집장이 작성한 글의 ID
            delay_seconds: AI 간 호출 간격 (초). API 부하 방지용.

        Returns:
            [{"display_name": "제미나이", "comment_id": 5, "content": "..."}, ...]
        """
        # 원글 가져오기
        post = self._reader.get_post(post_id)
        post_title = post.get("title", "")
        post_content = post.get("content", "")

        results = []
        # 누적 댓글 컨텍스트 — 다음 AI가 이전 댓글을 볼 수 있도록
        prior_comments = []

        for staff in self.staff:
            display_name = staff["display_name"]
            try:
                # 1. 두뇌 + 팔 준비
                brain = AIBrain(model=staff["model"])
                writer = AIWriter(base_url=BOARD_API_URL)
                writer.login(staff["username"], staff["password"])

                # 2. 댓글 생성 (원글 + 이전 댓글 컨텍스트 전달)
                reply = brain.write_discussion_comment(
                    display_name=display_name,
                    personality=staff["personality"],
                    post_title=post_title,
                    post_content=post_content,
                    prior_comments=prior_comments,
                )

                # 3. 댓글 등록
                comment = writer.write_comment(
                    post_id=post_id,
                    content=reply["content"],
                )
                comment_id = comment.get("id")

                results.append({
                    "display_name": display_name,
                    "comment_id": comment_id,
                    "content": reply["content"],
                })

                # 4. 다음 AI에게 전달할 컨텍스트에 추가
                prior_comments.append({
                    "author": display_name,
                    "content": reply["content"],
                })

                # 5. 간격 대기
                if delay_seconds > 0:
                    time.sleep(delay_seconds)

            except (AIBrainError, AIWriterError) as e:
                results.append({
                    "display_name": display_name,
                    "comment_id": None,
                    "error": str(e),
                })

        return results

    def run_discussion_for_posts(self, post_ids: list, delay_seconds: int = 5) -> dict:
        """
        여러 게시글에 대해 순차적으로 토론을 진행한다.
        06호에서 편집장이 2개 뉴스를 포스트했으므로 둘 다에 토론을 진행.

        Returns:
            {post_id: [댓글 결과 리스트], ...}
        """
        all_results = {}
        for post_id in post_ids:
            all_results[post_id] = self.run_discussion(post_id, delay_seconds)
        return all_results
