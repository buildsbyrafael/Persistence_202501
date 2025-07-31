from .user import router as user_router
from .post import router as post_router
from .comment import router as comment_router
from .category import router as category_router
from .like import router as like_router

__all__ = [
    "user_router",
    "post_router",
    "comment_router",
    "category_router",
    "like_router"
]