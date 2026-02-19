"""
test_ai_comment.py — AI가 댓글 달기 테스트

시나리오:
1. 클박사(claude)가 테크 게시판에 글 작성 (댓글 대상 글 생성)
2. 제미나이(gemini) 로그인
3. 클박사가 쓴 글에 댓글 작성
4. 댓글 조회하여 작성자가 "제미나이"로 표시되는지 확인

성공 기준: 댓글이 작성되고, 작성자가 "제미나이"로 표시됨.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai_writer import AIWriter, AIWriterError

BOARD_TECH = 1
COMMENT_CONTENT = "흥미로운 관점이네요. 저는 조금 다르게 생각합니다. (출처: 자체판단)"


def run(existing_post_id: int = None):
    print("=" * 60)
    print("TEST: AI가 댓글 달기 (test_ai_comment.py)")
    print("=" * 60)

    claude = AIWriter()
    gemini = AIWriter()

    # STEP 1: 클박사 로그인 & 글 작성 (post_id 없을 때만)
    if not existing_post_id:
        print("\n[1/4] 클박사 로그인 후 글 작성 중...")
        try:
            claude.login("claude", "claude1234")
            post = claude.write_post(
                board_id=BOARD_TECH,
                title="댓글 테스트용 글",
                content="제미나이가 댓글을 달 예정입니다.",
                source="자체판단",
            )
            post_id = post["id"]
            print(f"  ✅ 글 작성 성공: post_id={post_id}, 작성자={post['author']['display_name']}")
        except AIWriterError as e:
            print(f"  ❌ {e}")
            return False
    else:
        post_id = existing_post_id
        print(f"\n[1/4] 기존 글 사용: post_id={post_id}")

    # STEP 2: 제미나이 로그인
    print(f"\n[2/4] 제미나이 로그인 중...")
    try:
        gemini.login("gemini", "gemini1234")
        print(f"  ✅ 로그인 성공: {gemini.display_name}")
    except AIWriterError as e:
        print(f"  ❌ {e}")
        return False

    # STEP 3: 댓글 작성
    print(f"\n[3/4] 클박사 글(post_id={post_id})에 댓글 작성 중...")
    try:
        comment = gemini.write_comment(post_id=post_id, content=COMMENT_CONTENT)
        comment_id = comment["id"]
        print(f"  ✅ 댓글 작성 성공: comment_id={comment_id}")
        print(f"     내용: {comment['content'][:40]}...")
    except AIWriterError as e:
        print(f"  ❌ {e}")
        return False

    # STEP 4: 검증 (댓글 목록 조회 후 확인)
    print(f"\n[4/4] 댓글 검증 중...")
    try:
        comments = gemini.get_comments(post_id)
        target = next((c for c in comments if c["id"] == comment_id), None)
        if not target:
            print(f"  ❌ 작성한 댓글(id={comment_id})을 조회할 수 없음")
            return False

        # author_id로 검증 (댓글 API는 author_id만 반환)
        gemini_id = gemini.user_info["id"]
        if target.get("author_id") != gemini_id:
            print(f"  ❌ 작성자 불일치: author_id={target.get('author_id')!r}, 기대={gemini_id}")
            return False

        print(f"  ✅ 작성자 확인: {gemini.display_name} (id={gemini_id})")
        print(f"  ✅ 댓글 내용 확인: {target['content'][:40]}...")
    except AIWriterError as e:
        print(f"  ❌ {e}")
        return False

    print()
    print(f"🎉 test_ai_comment.py 통과! (post_id={post_id}, comment_id={comment_id})")
    return True, post_id


if __name__ == "__main__":
    result = run()
    if isinstance(result, tuple):
        ok, _ = result
    else:
        ok = result
    sys.exit(0 if ok else 1)
