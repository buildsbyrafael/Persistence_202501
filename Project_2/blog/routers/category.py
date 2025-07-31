from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from sqlalchemy import func

from models import Category
from schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from schemas.utils import CountResponse
from core.dependencies import get_session
from loguru import logger

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryRead)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    logger.info(f"Creating category: {category.name}")
    db_category = Category.from_orm(category)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.get("/", response_model=List[CategoryRead])
def read_categories(
    session: Session = Depends(get_session),
    name: Optional[str] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    logger.info(f"Reading categories with offset={offset}, limit={limit}, name={name}, "
                f"created_after={created_after}, created_before={created_before}")

    query = select(Category)

    if name:
        query = query.where(Category.name.contains(name))

    if created_after:
        query = query.where(Category.created_at >= created_after)
    if created_before:
        query = query.where(Category.created_at < created_before)

    categories = session.exec(
        query.offset(offset).limit(limit)
    ).all()

    return categories

@router.get("/{category_id}", response_model=CategoryRead)
def read_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=CategoryRead)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    session: Session = Depends(get_session)
):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category_data = category_update.dict(exclude_unset=True)
    for key, value in category_data.items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    logger.info(f"Updating category {category_id}")
    return category

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, session: Session = Depends(get_session)):
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    session.delete(category)
    session.commit()
    logger.info(f"Deleting category {category_id}")
    return None

@router.get("/metrics/count", response_model=CountResponse)
def count_categories(session: Session = Depends(get_session)):
    quantidade = session.exec(select(func.count(Category.id))).one()
    return CountResponse(quantidade=quantidade)