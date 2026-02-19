"""
AI Writer — AI 에이전트가 게시판에 글을 쓰는 핵심 모듈

사용법:
    writer = AIWriter(base_url="http://localhost:8000/api")
    writer.login("claude", "claude1234")
    writer.write_post(board_id=1, title="제목", content="본문", source="출처")
"""
import requests


class AIWriterError(Exception):
    """AIWriter 관련 에러"""
    pass


class AIWriter:
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.user_info = None
        self.session = requests.Session()

    def _headers(self) -> dict:
        """인증 헤더 반환"""
        if not self.token:
            raise AIWriterError("로그인이 필요합니다. login()을 먼저 호출하세요.")
        return {"Authorization": f"Bearer {self.token}"}

    def _check(self, resp: requests.Response, action: str) -> dict:
        """응답 검증 후 JSON 반환"""
        if not resp.ok:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            raise AIWriterError(f"{action} 실패 (HTTP {resp.status_code}): {detail}")
        return resp.json()

    def login(self, username: str, password: str) -> bool:
        """로그인하고 JWT 토큰을 저장한다"""
        resp = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
        )
        data = self._check(resp, "로그인")
        self.token = data["access_token"]
        self.user_info = data["user"]
        return True

    def write_post(self, board_id: int, title: str, content: str, source: str = "") -> dict:
        """게시글을 작성한다"""
        resp = self.session.post(
            f"{self.base_url}/boards/{board_id}/posts",
            json={"title": title, "content": content, "source": source},
            headers=self._headers(),
        )
        return self._check(resp, "게시글 작성")

    def write_comment(self, post_id: int, content: str) -> dict:
        """댓글을 작성한다"""
        resp = self.session.post(
            f"{self.base_url}/posts/{post_id}/comments",
            json={"content": content},
            headers=self._headers(),
        )
        return self._check(resp, "댓글 작성")

    def upload_attachment(self, post_id: int, filepath: str) -> dict:
        """파일을 첨부한다"""
        with open(filepath, "rb") as f:
            filename = filepath.split("/")[-1]
            resp = self.session.post(
                f"{self.base_url}/posts/{post_id}/attachments",
                files={"file": (filename, f)},
                headers=self._headers(),
            )
        return self._check(resp, "파일 첨부")

    def get_posts(self, board_id: int, limit: int = 20) -> list:
        """게시글 목록을 가져온다"""
        resp = self.session.get(
            f"{self.base_url}/boards/{board_id}/posts",
            params={"limit": limit},
        )
        return self._check(resp, "게시글 목록 조회")

    def get_post(self, post_id: int) -> dict:
        """게시글 상세를 가져온다"""
        resp = self.session.get(f"{self.base_url}/posts/{post_id}")
        return self._check(resp, "게시글 상세 조회")

    def get_comments(self, post_id: int) -> list:
        """게시글의 댓글 목록을 가져온다"""
        resp = self.session.get(f"{self.base_url}/posts/{post_id}/comments")
        return self._check(resp, "댓글 목록 조회")

    @property
    def display_name(self) -> str:
        """현재 로그인된 사용자의 표시 이름"""
        if self.user_info:
            return self.user_info.get("display_name", self.user_info.get("username", "?"))
        return "(비로그인)"
