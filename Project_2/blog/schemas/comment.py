from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    post_id: int
    author_id: int


class CommentRead(CommentBase):
    id: int
    created_at: datetime
    post_id: int
    author_id: int

    class Config:
        orm_mode = True


class CommentUpdate(BaseModel):
    content: Optional[str] = None