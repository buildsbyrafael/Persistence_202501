from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime


class Like(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reaction: str = Field(default="like", nullable=False)
    ip_address: Optional[str] = Field(default=None)

    # Chaves estrangeiras
    user_id: int = Field(foreign_key="user.id")
    post_id: int = Field(foreign_key="post.id")

    # Relacionamentos
    user: "User" = Relationship(back_populates="likes")
    post: "Post" = Relationship(back_populates="likes")