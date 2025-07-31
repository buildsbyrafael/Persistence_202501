from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2+


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    updated_at: Optional[datetime] = None