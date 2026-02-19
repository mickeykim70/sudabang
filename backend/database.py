from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from config import DATABASE_URL
from models import Base

# Async 엔진 생성 (SQLite는 기본 풀링 비활성화)
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # SQL 로그 비활성화 (True로 변경 시 SQL 쿼리 출력)
    poolclass=NullPool,
    future=True,
)

# Async 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db():
    """DB 테이블 초기화"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    """의존성 주입용 세션 제공"""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
