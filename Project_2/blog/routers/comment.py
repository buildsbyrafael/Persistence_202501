from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

from models import Comment, Post, User
from schemas.comment import CommentCreate, CommentRead, CommentUpdate
from schemas.utils import CountResponse
from core.dependencies import get_session
from loguru import logger

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentRead)
def create_comment(comment: CommentCreate, session: Session = Depends(get_session)):
    logger.info(f"Creating a comment on the post {comment.post_id}")

    post = session.get(Post, comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    author = session.get(User, comment.author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    existing_comment = session.exec(
        select(Comment).where(
            Comment.post_id == comment.post_id,
            Comment.author_id == comment.author_id,
            Comment.content == comment.content
        )
    ).first()
    if existing_comment:
        raise HTTPException(
            status_code=400,
            detail="Duplicate comment content by the same user on this post is not allowed."
        )

    db_comment = Comment.from_orm(comment)
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)

    return db_comment

@router.get("/", response_model=List[CommentRead])
def read_comments(
    session: Session = Depends(get_session),
    post_id: Optional[int] = None,
    author_id: Optional[int] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    logger.info(
        f"Lendo comentários com offset={offset}, limit={limit}, "
        f"post_id={post_id}, author_id={author_id}, "
        f"created_after={created_after}, created_before={created_before}"
    )

    query = select(Comment)

    if post_id:
        query = query.where(Comment.post_id == post_id)

    if author_id:
        query = query.where(Comment.author_id == author_id)

    if created_after:
        query = query.where(Comment.created_at >= created_after)
    if created_before:
        query = query.where(Comment.created_at < created_before)

    comments = session.exec(
        query.offset(offset).limit(limit)
    ).all()

    return comments

@router.get("/{comment_id}", response_model=CommentRead)
def read_comment(comment_id: int, session: Session = Depends(get_session)):
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment

@router.put("/{comment_id}", response_model=CommentRead)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    session: Session = Depends(get_session)
):
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment_data = comment_update.dict(exclude_unset=True)

    new_content = comment_data.get("content")
    if new_content and new_content != comment.content:
        existing_comment = session.exec(
            select(Comment).where(
                Comment.post_id == comment.post_id,
                Comment.author_id == comment.author_id,
                Comment.content == new_content
            )
        ).first()
        if existing_comment:
            raise HTTPException(
                status_code=400,
                detail="Duplicate comment content by the same user on this post is not allowed."
            )

    for key, value in comment_data.items():
        setattr(comment, key, value)

    session.add(comment)
    session.commit()
    session.refresh(comment)
    logger.info(f"Updating comment {comment_id}")
    return comment

@router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: int, session: Session = Depends(get_session)):
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    session.delete(comment)
    session.commit()
    logger.info(f"Deleting comment {comment_id}")
    return None

@router.get("/metrics/count", response_model=CountResponse)
def count_comments(session: Session = Depends(get_session)):
    quantidade = session.exec(select(func.count(Comment.id))).one()
    return CountResponse(quantidade=quantidade)