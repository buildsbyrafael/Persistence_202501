from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False, unique=True)
    email: str = Field(index=True, nullable=False, unique=True)
    full_name: Optional[str]
    bio: Optional[str]
    created_at: Optional[str] = Field(default=None)

    # Relacionamentos 1:N
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")
    likes: List["Like"] = Relationship(back_populates="user")