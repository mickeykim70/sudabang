# 라우터들을 main.py에서 쉽게 import하기 위한 패키지 초기화
from . import auth_router
from . import board_router
from . import post_router
from . import comment_router

from . import attachment_router

__all__ = ["auth_router", "board_router", "post_router", "comment_router", "attachment_router"]
