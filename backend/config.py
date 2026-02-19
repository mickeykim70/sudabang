import os
from pathlib import Path

# 프로젝트 루트
PROJECT_ROOT = Path(__file__).parent.parent

# 데이터베이스
DATABASE_URL = f"sqlite+aiosqlite:///{PROJECT_ROOT}/data/board.db"

# JWT 설정
SECRET_KEY = "sudabang-secret-key-2026"  # 프로덕션: 환경변수로 변경 필요
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24시간

# 파일 업로드
UPLOADS_DIR = PROJECT_ROOT / "uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 파일 디렉토리 확인
os.makedirs(UPLOADS_DIR, exist_ok=True)
