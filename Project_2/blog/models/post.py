from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class PostCategoryLink(SQLModel, table=True):
    post_id: Optional[int] = Field(default=None, foreign_key="post.id", primary_key=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", primary_key=True)


class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, index=True)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    author_id: int = Field(foreign_key="user.id")

    # Relacionamentos
    author: "User" = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    categories: List["Category"] = Relationship(
        back_populates="posts",
        link_model=PostCategoryLink
    )
    likes: List["Like"] = Relationship(back_populates="post")
