from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models import Role


# ==================== 사용자 스키마 ====================
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    display_name: str = Field(..., min_length=1, max_length=100)
    role: Role = Role.MEMBER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== 게시판 스키마 ====================
class BoardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class BoardCreate(BoardBase):
    pass


class BoardUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class BoardResponse(BoardBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 게시글 스키마 ====================
class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    source: Optional[str] = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None


class PostResponse(PostBase):
    id: int
    board_id: int
    author_id: int
    author: UserResponse
    board: BoardResponse
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostDetailResponse(PostResponse):
    comments: List["CommentResponse"] = []
    attachments: List["AttachmentResponse"] = []


# ==================== 댓글 스키마 ====================
class CommentBase(BaseModel):
    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    post_id: int
    author_id: int
    author: UserResponse
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 첨부파일 스키마 ====================
class AttachmentResponse(BaseModel):
    id: int
    post_id: int
    filename: str
    file_type: str
    file_size: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 검색 스키마 ====================
class SearchResponse(BaseModel):
    posts: List[PostResponse] = []
    total: int = 0


# 순환 참조 해결
PostDetailResponse.model_rebuild()
