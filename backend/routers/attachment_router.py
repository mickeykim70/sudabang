from fastapi import APIRouter, Depends, HTTPException, status, Header, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import os

from database import get_session
from models import Attachment, Post, User
from schemas import AttachmentResponse
from auth import decode_token
from config import UPLOADS_DIR, MAX_FILE_SIZE

router = APIRouter(prefix="/api", tags=["attachments"])


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


@router.post("/posts/{post_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    post_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """파일 업로드 (인증 필요)"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    # 게시글 존재 확인
    stmt = select(Post).where(Post.id == post_id)
    post = await session.execute(stmt)
    post = post.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # 파일 크기 확인
    file.file.seek(0, 2)  # 파일 끝으로 이동
    file_size = file.file.tell()
    file.file.seek(0)  # 파일 시작으로 이동

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit"
        )

    # 디렉토리 생성
    upload_path = UPLOADS_DIR / str(post_id)
    os.makedirs(upload_path, exist_ok=True)

    # 파일 저장
    filename = file.filename
    stored_path = upload_path / filename

    try:
        with open(stored_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )

    # DB에 첨부파일 정보 저장
    attachment = Attachment(
        post_id=post_id,
        filename=filename,
        stored_path=str(stored_path),
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size,
    )
    session.add(attachment)
    await session.commit()
    await session.refresh(attachment)

    return attachment


@router.get("/attachments/{attachment_id}")
async def download_attachment(
    attachment_id: int,
    session: AsyncSession = Depends(get_session)
):
    """파일 다운로드 (공개)"""
    stmt = select(Attachment).where(Attachment.id == attachment_id)
    attachment = await session.execute(stmt)
    attachment = attachment.scalar_one_or_none()

    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )

    # 파일 존재 확인
    file_path = Path(attachment.stored_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )

    return FileResponse(
        path=file_path,
        filename=attachment.filename,
        media_type=attachment.file_type
    )
