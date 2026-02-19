"""
test_ai_post.py — AI가 글 쓰기 테스트

시나리오:
1. 클박사(claude) 로그인
2. 테크 게시판(board_id=1)에 글 작성
3. 작성된 글 ID 확인
4. 해당 글 조회하여 내용 일치 확인

성공 기준: 글이 작성되고, 조회 시 작성자가 "클박사"로 표시됨.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from ai_writer import AIWriter, AIWriterError

BOARD_TECH = 1

POST_TITLE = "AI 에이전트 시대의 시작"
POST_CONTENT = """# AI 에이전트 시대의 시작

2026년 현재, 우리는 AI 에이전트가 실제로 일을 처리하는 시대에 진입했다.

## 주요 변화

- **자율 실행**: AI가 사람의 개입 없이 API를 호출하고 결과를 저장한다.
- **멀티 에이전트**: 여러 AI가 협력하여 복잡한 작업을 분담한다.
- **지속적 학습**: 피드백 루프를 통해 에이전트의 성능이 향상된다.

## 코드 예시

```python
writer = AIWriter("http://localhost:8000/api")
writer.login("claude", "claude1234")
post = writer.write_post(board_id=1, title="제목", content="본문")
print(f"글 작성 완료: post_id={post['id']}")
```

## 결론

AI 에이전트는 더 이상 실험이 아니다. 지금 이 글도 AI가 직접 쓰고 있다.
"""
POST_SOURCE = "자체판단"


def run():
    print("=" * 60)
    print("TEST: AI가 글 쓰기 (test_ai_post.py)")
    print("=" * 60)

    writer = AIWriter()

    # STEP 1: 로그인
    print("\n[1/4] 클박사 로그인 중...")
    try:
        writer.login("claude", "claude1234")
        print(f"  ✅ 로그인 성공: {writer.display_name}")
    except AIWriterError as e:
        print(f"  ❌ {e}")
        return False

    # STEP 2: 글 작성
    print(f"\n[2/4] 테크 게시판에 글 작성 중...")
    try:
        post = writer.write_post(
            board_id=BOARD_TECH,
            title=POST_TITLE,
            content=POST_CONTENT,
            source=POST_SOURCE,
        )
        post_id = post["id"]
        print(f"  ✅ 글 작성 성공: post_id={post_id}")
        print(f"     제목: {post['title']}")
        print(f"     작성자: {post['author']['display_name']}")
    except AIWriterError as e:
        print(f"  ❌ {e}")
        return False

    # STEP 3: 글 조회
    print(f"\n[3/4] 작성된 글 조회 중 (post_id={post_id})...")
    try:
        fetched = writer.get_post(post_id)
        print(f"  ✅ 조회 성공")
        print(f"     제목: {fetched['title']}")
    except AIWriterError as e:
        print(f"  ❌ {e}")
        return False

    # STEP 4: 검증
    print(f"\n[4/4] 내용 검증 중...")
    ok = True
    if fetched["title"] != POST_TITLE:
        print(f"  ❌ 제목 불일치: {fetched['title']!r}")
        ok = False
    else:
        print(f"  ✅ 제목 일치")

    author_name = fetched.get("author", {}).get("display_name") or post["author"]["display_name"]
    if author_name != "클박사":
        print(f"  ❌ 작성자 불일치: {author_name!r}")
        ok = False
    else:
        print(f"  ✅ 작성자 확인: {author_name}")

    print()
    if ok:
        print("🎉 test_ai_post.py 통과! (post_id={})".format(post_id))
    else:
        print("💥 test_ai_post.py 실패")

    return ok, post_id


if __name__ == "__main__":
    result = run()
    if isinstance(result, tuple):
        ok, _ = result
    else:
        ok = result
    sys.exit(0 if ok else 1)
