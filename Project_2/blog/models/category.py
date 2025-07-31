from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from models.post import PostCategoryLink

class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True, index=True)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # Relacionamento N:N com Post
    posts: List["Post"] = Relationship(
        back_populates="categories",
        link_model=PostCategoryLink
    )