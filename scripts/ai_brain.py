"""
AI 두뇌 — OpenRouter를 통해 다양한 AI 모델 호출

사용법:
    brain = AIBrain(model="anthropic/claude-sonnet-4-5-20250929")
    result = brain.write_article(topic="AI 트렌드", board_name="테크")

핵심: self.model만 바꾸면 Claude, Gemini, GPT, Grok 어떤 두뇌든 사용 가능.
"""
import json
import time
from openai import OpenAI, APIStatusError, APIConnectionError
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL


class AIBrainError(Exception):
    pass


class AIBrain:
    def __init__(self, model: str = "anthropic/claude-sonnet-4.5", api_key: str = None):
        """
        model: OpenRouter 모델명 (예: "anthropic/claude-sonnet-4-5-20250929")
        api_key: 하위 호환용 (무시됨, 환경변수 OPENROUTER_API_KEY 사용)
        """
        self.model = model
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
        )

    def _call(self, system: str, user: str, max_retries: int = 3) -> str:
        """OpenRouter API 호출 (최대 3회 재시도)"""
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                return response.choices[0].message.content
            except APIStatusError as e:
                if e.status_code == 402:
                    raise AIBrainError("API 요금 부족. OpenRouter 크레딧 충전 후 다시 시도하세요.")
                if attempt == max_retries:
                    raise AIBrainError(f"API 호출 실패 ({max_retries}회 재시도 후): {e}")
                time.sleep(2 ** attempt)
            except APIConnectionError as e:
                if attempt == max_retries:
                    raise AIBrainError(f"네트워크 오류 ({max_retries}회 재시도 후): {e}")
                time.sleep(2 ** attempt)

    def _parse_json(self, text: str) -> dict:
        """응답에서 JSON 파싱 (코드블록 제거 후 시도)"""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise AIBrainError(f"응답 파싱 실패: {e}\n원본: {text[:200]}")

    def write_article(self, topic: str, board_name: str, context: str = "") -> dict:
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
        context_part = f"\n\n참고 맥락:\n{context}" if context else ""
        user = (
            f"게시판: {board_name}\n"
            f"주제: {topic}{context_part}\n\n"
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

    def select_news(self, headlines: list, max_count: int = 2) -> list:
        """
        헤드라인 목록에서 중요한 뉴스를 선별한다.

        반환값:
        [{"index": 0, "title": "...", "reason": "..."}, ...]
        """
        headlines_text = "\n".join(
            f"{i}. [{item.get('source_name', item.get('source', '뉴스'))}] {item['title']}"
            for i, item in enumerate(headlines)
        )
        system = (
            "You are the editor-in-chief of '수다방', an AI community news board. "
            "Select the most valuable news for Korean readers."
        )
        user = (
            f"다음 헤드라인 중 독자에게 가장 가치 있는 뉴스를 {max_count}개 골라라.\n\n"
            f"선택 기준:\n"
            f"- 경제적 영향력 (한국 경제에 직접 영향)\n"
            f"- 기술적 중요성 (AI/테크 업계의 큰 변화)\n"
            f"- 시의성 (지금 가장 핫한 이슈)\n\n"
            f"헤드라인 목록:\n{headlines_text}\n\n"
            f"반드시 아래 JSON 형식으로만 응답해 (index는 0부터 시작):\n"
            f'[{{"index": 0, "title": "선택한 뉴스 제목", "reason": "선택 이유", "category": "tech 또는 economy"}}, ...]'
        )
        raw = self._call(system, user)
        result = self._parse_json(raw)
        # 리스트로 래핑된 경우도 처리
        if isinstance(result, dict):
            result = [result]
        return result

    def write_news_post(self, news_item: dict) -> dict:
        """
        선택된 뉴스에 대해 분석 포스트를 작성한다.

        반환값:
        {
            "title": "[테크] 뉴스 제목",
            "content": "마크다운 본문",
            "source": "출처 URL"
        }
        """
        category_label = "테크" if news_item.get("category") == "tech" else "경제"
        system = (
            "You are the editor-in-chief of '수다방', an AI community board in Korea. "
            "Write insightful news analysis posts in Korean."
        )
        user = (
            f"다음 뉴스에 대해 수다방 커뮤니티 분석 게시글을 작성해라.\n\n"
            f"뉴스 제목: {news_item['title']}\n"
            f"출처: {news_item.get('source_name', '뉴스')}\n"
            f"링크: {news_item.get('link', '')}\n"
            f"카테고리: {category_label}\n\n"
            f"작성 규칙:\n"
            f"- 제목은 반드시 [{category_label}] 로 시작\n"
            f"- 한국어로 작성\n"
            f"- 마크다운 형식 (## 소제목, **강조** 등)\n"
            f"- 3~5문단 분량\n"
            f"- 뉴스의 배경, 의미, 영향을 분석\n"
            f"- 마지막 문단은 반드시 \"**편집장 의견:**\" 으로 시작하는 개인 의견 포함\n"
            f"- 출처 URL 반드시 포함\n\n"
            f"반드시 아래 JSON 형식으로만 응답해:\n"
            '{{"title": "[카테고리] 제목", "content": "마크다운 본문", "source": "출처URL"}}'
        )
        raw = self._call(system, user)
        return self._parse_json(raw)
