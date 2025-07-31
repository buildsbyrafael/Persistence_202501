from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Chaves estrangeiras
    post_id: int = Field(foreign_key="post.id")
    author_id: int = Field(foreign_key="user.id")

    # Relacionamentos
    post: "Post" = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="comments")