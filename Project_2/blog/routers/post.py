from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from models import Post, PostCategoryLink, User, Category
from schemas.post import PostCreate, PostRead, PostUpdate
from schemas.utils import CountResponse
from core.dependencies import get_session
from loguru import logger

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/", response_model=PostRead)
def create_post(post: PostCreate, session: Session = Depends(get_session)):
    if not post.category_ids:
        raise HTTPException(
            status_code=400,
            detail="At least one category must be provided."
        )

    author = session.exec(select(User).where(User.id == post.author_id)).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    existing_post = session.exec(
        select(Post).where(Post.title == post.title, Post.author_id == post.author_id)
    ).first()
    if existing_post:
        raise HTTPException(
            status_code=400,
            detail="A post with this title already exists for this author."
        )

    categories = session.exec(
        select(Category).where(Category.id.in_(post.category_ids))
    ).all()

    found_ids = {cat.id for cat in categories}
    missing_ids = set(post.category_ids) - found_ids

    if missing_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Categories not found: {sorted(list(missing_ids))}"
        )

    db_post = Post(
        title=post.title,
        content=post.content,
        author_id=post.author_id
    )
    session.add(db_post)
    session.commit()
    session.refresh(db_post)

    for category_id in post.category_ids:
        link = PostCategoryLink(post_id=db_post.id, category_id=category_id)
        session.add(link)

    session.commit()

    db_post = session.exec(
        select(Post).where(Post.id == db_post.id).options(selectinload(Post.categories))
    ).first()

    return PostRead.from_orm_with_categories(db_post)

@router.get("/", response_model=List[PostRead])
def read_posts(
    session: Session = Depends(get_session),
    title: Optional[str] = None,
    author_id: Optional[int] = None,
    category_id: Optional[int] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    logger.info(
        f"Reading posts with offset={offset}, limit={limit}, "
        f"title={title}, author_id={author_id}, category_id={category_id}, "
        f"created_after={created_after}, created_before={created_before}"
    )

    query = select(Post).options(selectinload(Post.categories))

    if title:
        query = query.where(Post.title.contains(title))
    if author_id:
        query = query.where(Post.author_id == author_id)
    if category_id:
        query = query.join(PostCategoryLink).where(PostCategoryLink.category_id == category_id)
    if created_after:
        query = query.where(Post.created_at >= created_after)
    if created_before:
        query = query.where(Post.created_at < created_before)

    posts = session.exec(query.offset(offset).limit(limit)).all()
    return [PostRead.from_orm_with_categories(p) for p in posts]

@router.get("/{post_id}", response_model=PostRead)
def read_post(post_id: int, session: Session = Depends(get_session)):
    post = session.exec(
        select(Post).where(Post.id == post_id).options(selectinload(Post.categories))
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return PostRead.from_orm_with_categories(post)

@router.put("/{post_id}", response_model=PostRead)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    session: Session = Depends(get_session)
):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_data = post_update.dict(exclude_unset=True, exclude={"category_ids"})
    for key, value in post_data.items():
        setattr(post, key, value)

    if post_update.category_ids is not None:
        categories = session.exec(
            select(Category).where(Category.id.in_(post_update.category_ids))
        ).all()

        found_ids = {cat.id for cat in categories}
        missing_ids = set(post_update.category_ids) - found_ids

        if missing_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Categories not found: {sorted(list(missing_ids))}"
            )

        session.query(PostCategoryLink).filter(PostCategoryLink.post_id == post_id).delete()

        for category_id in post_update.category_ids:
            link = PostCategoryLink(post_id=post_id, category_id=category_id)
            session.add(link)

    session.add(post)
    session.commit()

    post = session.exec(
        select(Post).where(Post.id == post_id).options(selectinload(Post.categories))
    ).first()

    logger.info(f"Updating post {post_id}")
    return PostRead.from_orm_with_categories(post)

@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, session: Session = Depends(get_session)):
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    session.delete(post)
    session.commit()
    logger.info(f"Deleting post {post_id}")
    return None

@router.get("/metrics/count", response_model=CountResponse)
def count_posts(session: Session = Depends(get_session)):
    quantidade = session.exec(select(func.count(Post.id))).one()
    return CountResponse(quantidade=quantidade)