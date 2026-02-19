from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from typing import List

from database import get_session
from models import Post, Board, User, Role
from schemas import PostCreate, PostUpdate, PostResponse, PostDetailResponse
from auth import decode_token

router = APIRouter(prefix="/api", tags=["posts"])


async def get_current_user(authorization: str = Header(None), session: AsyncSession = Depends(get_session)):
    """Authorization 헤더에서 토큰 추출 후 사용자 조회"""
    if not authorization:
        return None
    
    try:
        token = authorization.split(" ")[1]  # "Bearer <token>"
    except IndexError:
        return None
    
    payload = decode_token(token)
    if not payload:
        return None
    
    user_id = int(payload.get("sub"))
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


@router.get("/boards/{board_id}/posts")
async def list_posts_by_board(
    board_id: int,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """게시판 내 게시글 목록 (최신순, 공개)"""
    # 게시판 존재 확인
    stmt = select(Board).where(and_(Board.id == board_id, Board.is_active == True))
    board = await session.execute(stmt)
    if not board.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    # 게시글 조회
    stmt = select(Post).where(
        Post.board_id == board_id
    ).order_by(desc(Post.created_at)).limit(limit).offset(offset)
    
    result = await session.execute(stmt)
    posts = result.scalars().all()
    
    # 부분적 응답만 반환
    return posts


@router.get("/posts/{post_id}")
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_session)
):
    """게시글 상세 조회 + 조회수 증가 (공개)"""
    stmt = select(Post).where(Post.id == post_id)
    post = await session.execute(stmt)
    post = post.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 조회수 증가
    post.view_count += 1
    await session.commit()
    await session.refresh(post)
    
    return post


@router.post("/boards/{board_id}/posts", status_code=status.HTTP_201_CREATED)
async def create_post(
    board_id: int,
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """게시글 작성 (인증 필요)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # 게시판 존재 확인
    stmt = select(Board).where(and_(Board.id == board_id, Board.is_active == True))
    result = await session.execute(stmt)
    board_obj = result.scalar_one_or_none()
    if not board_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    new_post = Post(
        board_id=board_id,
        author_id=current_user.id,
        title=post_data.title,
        content=post_data.content,
        source=post_data.source,
    )
    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)
    
    # 응답 데이터 수동 구성 (SQLAlchemy 비동기 이슈 회피)
    return {
        "id": new_post.id,
        "board_id": new_post.board_id,
        "author_id": new_post.author_id,
        "title": new_post.title,
        "content": new_post.content,
        "source": new_post.source,
        "view_count": new_post.view_count,
        "created_at": new_post.created_at,
        "updated_at": new_post.updated_at,
        "author": {
            "id": current_user.id,
            "username": current_user.username,
            "display_name": current_user.display_name,
            "role": current_user.role.value,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
        },
        "board": {
            "id": board_obj.id,
            "name": board_obj.name,
            "slug": board_obj.slug,
            "description": board_obj.description,
            "is_active": board_obj.is_active,
            "created_at": board_obj.created_at,
        }
    }


@router.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """게시글 수정 (본인만)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    stmt = select(Post).where(Post.id == post_id)
    post = await session.execute(stmt)
    post = post.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 본인/관리자만 수정 가능
    if post.author_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    if post_data.title:
        post.title = post_data.title
    if post_data.content:
        post.content = post_data.content
    if post_data.source is not None:
        post.source = post_data.source
    
    await session.commit()
    await session.refresh(post)
    
    return post


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """게시글 삭제 (본인 + admin)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    stmt = select(Post).where(Post.id == post_id)
    post = await session.execute(stmt)
    post = post.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 본인/관리자만 삭제 가능
    if post.author_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    await session.delete(post)
    await session.commit()


@router.get("/search")
async def search_posts(
    q: str = Query(..., min_length=1),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
):
    """게시글 검색 (제목 + 본문, LIKE 검색)"""
    search_term = f"%{q}%"
    stmt = select(Post).where(
        or_(
            Post.title.ilike(search_term),
            Post.content.ilike(search_term)
        )
    ).order_by(desc(Post.created_at)).limit(limit)
    
    result = await session.execute(stmt)
    return result.scalars().all()
