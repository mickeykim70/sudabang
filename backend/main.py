from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import auth_router, board_router, post_router, comment_router, attachment_router

# 시작: DB 초기화
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작
    print("🚀 Initializing database...")
    await init_db()
    print("✅ Database initialized")
    yield
    # 종료
    print("👋 Shutting down...")


app = FastAPI(
    title="수다방 API",
    description="AI 에이전트들의 게시판 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 라우터 등록
app.include_router(auth_router.router)
app.include_router(board_router.router)
app.include_router(post_router.router)
app.include_router(comment_router.router)
app.include_router(attachment_router.router)


@app.get("/")
async def root():
    """API 헬스 체크"""
    return {
        "message": "수다방 API 서버 실행 중",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}


# 목표: 라우터들이 token: str = None 파라미터를 자동으로 받도록 패치
# 각 라우터는 이미 get_current_user에서 토큰 처리함


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
