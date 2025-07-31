from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    author_id: int
    category_ids: Optional[List[int]] = []


class PostRead(PostBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    author_id: int
    category_ids: List[int] = []

    @staticmethod
    def from_orm_with_categories(post_orm) -> "PostRead":
        return PostRead(
            id=post_orm.id,
            title=post_orm.title,
            content=post_orm.content,
            created_at=post_orm.created_at,
            updated_at=post_orm.updated_at,
            author_id=post_orm.author_id,
            category_ids=[cat.id for cat in getattr(post_orm, "categories", [])]
        )

    class Config:
        from_attributes = True  # Compatível com Pydantic v2


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_ids: Optional[List[int]] = []
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True