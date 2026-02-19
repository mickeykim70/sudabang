from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from typing import List

from database import get_session
from models import Comment, Post, User, Role
from schemas import CommentCreate, CommentResponse
from auth import decode_token

router = APIRouter(prefix="/api", tags=["comments"])


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


@router.get("/posts/{post_id}/comments")
async def list_comments(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(50, ge=1, le=100),
):
    """댓글 목록 조회 (공개)"""
    # 게시글 존재 확인
    stmt = select(Post).where(Post.id == post_id)
    post = await session.execute(stmt)
    if not post.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 댓글 조회
    stmt = select(Comment).where(
        Comment.post_id == post_id
    ).order_by(Comment.created_at).limit(limit)
    
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """댓글 작성 (인증 필요)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    # 게시글 존재 확인
    stmt = select(Post).where(Post.id == post_id)
    post = await session.execute(stmt)
    if not post.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    new_comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=comment_data.content,
    )
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    
    return new_comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """댓글 삭제 (본인 + admin)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    stmt = select(Comment).where(Comment.id == comment_id)
    comment = await session.execute(stmt)
    comment = comment.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # 본인/관리자만 삭제 가능
    if comment.author_id != current_user.id and current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied"
        )
    
    await session.delete(comment)
    await session.commit()
