from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

from models import Like, User, Post
from schemas.like import LikeCreate, LikeRead, LikeUpdate
from schemas.utils import CountResponse
from core.dependencies import get_session
from loguru import logger

router = APIRouter(prefix="/likes", tags=["Likes"])

@router.post("/", response_model=LikeRead)
def create_like(like: LikeCreate, session: Session = Depends(get_session)):
    logger.info(f"User {like.user_id} is liking post {like.post_id}")

    user = session.get(User, like.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    post = session.get(Post, like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = session.exec(
        select(Like).where(Like.user_id == like.user_id, Like.post_id == like.post_id)
    ).first()

    if existing_like:
        raise HTTPException(status_code=400, detail="This like already exists")

    db_like = Like.from_orm(like)
    session.add(db_like)
    session.commit()
    session.refresh(db_like)

    return db_like

@router.get("/", response_model=List[LikeRead])
def read_likes(
    session: Session = Depends(get_session),
    user_id: Optional[int] = None,
    post_id: Optional[int] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    logger.info(
        f"Reading likes with offset={offset}, limit={limit}, user_id={user_id}, post_id={post_id}, "
        f"created_after={created_after}, created_before={created_before}"
    )

    query = select(Like)

    if user_id:
        query = query.where(Like.user_id == user_id)

    if post_id:
        query = query.where(Like.post_id == post_id)

    if created_after:
        query = query.where(Like.created_at >= created_after)
    if created_before:
        query = query.where(Like.created_at < created_before)

    likes = session.exec(
        query.offset(offset).limit(limit)
    ).all()

    return likes

@router.get("/{like_id}", response_model=LikeRead)
def read_like(like_id: int, session: Session = Depends(get_session)):
    like = session.get(Like, like_id)
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    return like

@router.put("/{like_id}", response_model=LikeRead)
def update_like(
    like_id: int,
    like_update: LikeUpdate,
    session: Session = Depends(get_session)
):
    like = session.get(Like, like_id)
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    like_data = like_update.dict(exclude_unset=True)
    for key, value in like_data.items():
        setattr(like, key, value)

    session.add(like)
    session.commit()
    session.refresh(like)
    logger.info(f"Updating like {like_id}")
    return like

@router.delete("/{like_id}", status_code=204)
def delete_like(like_id: int, session: Session = Depends(get_session)):
    like = session.get(Like, like_id)
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    session.delete(like)
    session.commit()
    logger.info(f"Deleting like {like_id}")
    return None

@router.get("/metrics/count", response_model=CountResponse)
def count_likes(session: Session = Depends(get_session)):
    quantidade = session.exec(select(func.count(Like.id))).one()
    return CountResponse(quantidade=quantidade)