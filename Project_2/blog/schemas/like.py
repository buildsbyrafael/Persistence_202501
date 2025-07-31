from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LikeBase(BaseModel):
    reaction: str = "like"
    ip_address: Optional[str] = None


class LikeCreate(LikeBase):
    user_id: int
    post_id: int

    
class LikeUpdate(BaseModel):
    reaction: Optional[str] = None
    ip_address: Optional[str] = None


class LikeRead(LikeBase):
    id: int
    created_at: datetime
    user_id: int
    post_id: int


    class Config:
        from_attributes = True  # Atualizado para Pydantic v2+
