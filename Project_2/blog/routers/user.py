from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from typing import List, Optional
from sqlalchemy import func

from models import User
from schemas.user import UserCreate, UserRead, UserUpdate
from schemas.utils import CountResponse
from core.dependencies import get_session
from loguru import logger
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    logger.info(f"Creating user: {user.username}")

    db_user = User.from_orm(user)
    session.add(db_user)

    try:
        session.commit()
        session.refresh(db_user)
        return db_user

    except IntegrityError as e:
        session.rollback()

        if "UNIQUE constraint failed: user.email" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email is already in use.")
        elif "UNIQUE constraint failed: user.username" in str(e.orig):
            raise HTTPException(status_code=400, detail="Username is already in use.")

        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal error creating user.")

@router.get("/", response_model=List[UserRead])
def read_users(
    session: Session = Depends(get_session),
    username: Optional[str] = None,
    email: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    logger.info(
        f"Reading users with offset={offset}, limit={limit}, username={username}, email={email}"
    )

    query = select(User)

    if username:
        query = query.where(User.username.contains(username))

    if email:
        query = query.where(User.email.contains(email))

    users = session.exec(
        query.offset(offset).limit(limit)
    ).all()

    return users

@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session)
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = user_update.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    logger.info(f"Updating user {user_id}")
    return user

@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    session.delete(user)
    session.commit()
    logger.info(f"Deleting user {user_id}")
    return None

@router.get("/metrics/count", response_model=CountResponse)
def count_users(session: Session = Depends(get_session)):
    quantidade = session.exec(select(func.count(User.id))).one()
    return CountResponse(quantidade=quantidade)