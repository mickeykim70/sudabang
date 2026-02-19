from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List

from database import get_session
from models import Board, User, Role
from schemas import BoardCreate, BoardUpdate, BoardResponse
from auth import decode_token

router = APIRouter(prefix="/api/boards", tags=["boards"])


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


@router.get("")
async def list_boards(session: AsyncSession = Depends(get_session)):
    """게시판 목록 조회 (공개)"""
    stmt = select(Board).where(Board.is_active == True).order_by(Board.created_at)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_board(
    board_data: BoardCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """게시판 생성 (admin만)"""
    if not current_user or current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    
    # slug 중복 확인
    stmt = select(Board).where(Board.slug == board_data.slug)
    existing = await session.execute(stmt)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slug already exists"
        )
    
    new_board = Board(
        name=board_data.name,
        slug=board_data.slug,
        description=board_data.description,
    )
    session.add(new_board)
    await session.commit()
    await session.refresh(new_board)
    
    return new_board


@router.put("/{board_id}")
async def update_board(
    board_id: int,
    board_data: BoardUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """게시판 수정 (admin만)"""
    if not current_user or current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    
    stmt = select(Board).where(Board.id == board_id)
    board = await session.execute(stmt)
    board = board.scalar_one_or_none()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    if board_data.name:
        board.name = board_data.name
    if board_data.description:
        board.description = board_data.description
    
    await session.commit()
    await session.refresh(board)
    
    return board


@router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """게시판 삭제 (soft delete, admin만)"""
    if not current_user or current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required"
        )
    
    stmt = select(Board).where(Board.id == board_id)
    board = await session.execute(stmt)
    board = board.scalar_one_or_none()
    
    if not board:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found"
        )
    
    board.is_active = False
    await session.commit()
