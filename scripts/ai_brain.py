"""
AI 두뇌 — Claude API를 호출해서 글/댓글/요약을 생성한다.
"""
import json
import time
import anthropic


class AIBrainError(Exception):
    pass


class AIBrain:
    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        """
        model: 비용 절약을 위해 Haiku 사용 (Sonnet 대비 약 20배 저렴).
        품질이 부족하면 대표님 승인 후 Sonnet으로 변경.
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def _call(self, system: str, user: str, max_retries: int = 3) -> str:
        """Claude API 호출 (최대 3회 재시도)"""
        for attempt in range(1, max_retries + 1):
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                return message.content[0].text
            except anthropic.APIStatusError as e:
                if e.status_code == 402:
                    raise AIBrainError("API 요금 부족. 충전 후 다시 시도하세요.")
                if attempt == max_retries:
                    raise AIBrainError(f"API 호출 실패 ({max_retries}회 재시도 후): {e}")
                time.sleep(2 ** attempt)
            except anthropic.APIConnectionError as e:
                if attempt == max_retries:
                    raise AIBrainError(f"네트워크 오류 ({max_retries}회 재시도 후): {e}")
                time.sleep(2 ** attempt)

    def _parse_json(self, text: str) -> dict:
        """응답에서 JSON 파싱 (코드블록 제거 후 시도)"""
        # ```json ... ``` 블록 제거
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise AIBrainError(f"응답 파싱 실패: {e}\n원본: {text[:200]}")

    def write_article(self, topic: str, board_name: str) -> dict:
        """
        주제를 받아서 게시글을 생성한다.

        반환값:
        {
            "title": "생성된 제목",
            "content": "마크다운 본문",
            "source": "출처 또는 자체판단"
        }
        """
        system = (
            "You are an active member of '수다방', a Korean online community where AI agents discuss "
            "technology, economics, and daily life. Write naturally in Korean as a thoughtful community member."
        )
        user = (
            f"게시판: {board_name}\n"
            f"주제: {topic}\n\n"
            f"위 주제로 게시글을 작성해줘. 다음 규칙을 따라줘:\n"
            f"- 한국어로 작성\n"
            f"- 마크다운 형식 사용 (## 소제목, **강조** 등)\n"
            f"- 3~5문단 분량\n"
            f"- {board_name} 게시판 성격에 맞게 작성\n"
            f"- 출처가 있으면 URL, 없으면 \"자체판단\"으로 명시\n\n"
            f"반드시 아래 JSON 형식으로만 응답해:\n"
            f'{{"title": "제목", "content": "마크다운 본문", "source": "출처 또는 자체판단"}}'
        )
        raw = self._call(system, user)
        return self._parse_json(raw)

    def write_reply(self, original_post: str, board_name: str) -> dict:
        """
        다른 AI의 글을 읽고 댓글을 생성한다.

        반환값:
        {
            "content": "댓글 내용",
        }
        """
        system = (
            "You are an active member of '수다방', a Korean online community. "
            "You read others' posts carefully and respond with thoughtful comments in Korean."
        )
        user = (
            f"게시판: {board_name}\n\n"
            f"아래 글을 읽고 댓글을 작성해줘:\n\n"
            f"---\n{original_post[:1500]}\n---\n\n"
            f"댓글 작성 규칙:\n"
            f"- 한국어로 작성\n"
            f"- 원글의 핵심 포인트를 파악해서 반응\n"
            f"- 동의/반론/보충 중 하나의 입장을 명확히\n"
            f"- 근거를 들어 의견 제시\n"
            f"- 2~4문장 분량\n\n"
            f"반드시 아래 JSON 형식으로만 응답해:\n"
            f'{{"content": "댓글 내용"}}'
        )
        raw = self._call(system, user)
        return self._parse_json(raw)

    def summarize_thread(self, posts_and_comments: list) -> dict:
        """
        게시판의 글과 댓글을 읽고 요약글을 생성한다.

        반환값:
        {
            "title": "[요약] 제목",
            "content": "마크다운 요약 본문",
            "source": "게시판 토론 기반 자체정리"
        }
        """
        # 요약용 텍스트 구성 (너무 길면 자름)
        thread_text = ""
        for item in posts_and_comments[:5]:
            title = item.get("title", "")
            content = item.get("content", "")[:500]
            author = item.get("author", {}).get("display_name", "?")
            thread_text += f"[{author}] {title}\n{content}\n\n"

        system = (
            "You are a summarizer in '수다방', a Korean online community. "
            "You read discussion threads and write concise, insightful summaries in Korean."
        )
        user = (
            f"아래 수다방 토론 내용을 읽고 요약 게시글을 작성해줘:\n\n"
            f"---\n{thread_text}\n---\n\n"
            f"요약글 규칙:\n"
            f"- 한국어로 작성\n"
            f"- 마크다운 형식 사용\n"
            f"- 제목은 반드시 [요약] 로 시작\n"
            f"- 주요 논점과 결론을 3~5문단으로 정리\n"
            f"- 출처는 항상 \"게시판 토론 기반 자체정리\"\n\n"
            f"반드시 아래 JSON 형식으로만 응답해:\n"
            f'{{"title": "[요약] 제목", "content": "마크다운 요약 본문", "source": "게시판 토론 기반 자체정리"}}'
        )
        raw = self._call(system, user)
        return self._parse_json(raw)
