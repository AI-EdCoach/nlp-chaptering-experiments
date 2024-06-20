from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import delete, func, select
from typing import List
from backend import crud
from backend.api.v1.dependencies import (
    SessionDep,
    CurrentUserDep,
    get_current_active_superuser,
)

from backend.core.config import settings
from backend.crud import get_user_predictions
from backend.core.security import get_password_hash, verify_password
from backend.schemas.user import UserCreateSchema, UserUpdateSchema, UserReadSchema
from backend.schemas.prediction import PredictionOutSchema
from backend.models import User
from backend.schemas.auth import TokenPayload
from backend.schemas.user import UserReadSchema


router = APIRouter()


@router.get(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=List[User]
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    statment = select(func.count()).select_from(User)
    count = session.exec(statment).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return List[User]


@router.get("/me", response_model=UserReadSchema)
def read_user_me(session: SessionDep, current_user: CurrentUserDep) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserReadSchema,
)
def read_user_by_id(
    user_id: int,
    session: SessionDep,
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserReadSchema,
)
def update_user(
    *,
    session: SessionDep,
    user_id: int,
    user_in: UserUpdateSchema,
) -> Any:
    """
    Update a user.
    """

    db_user = crud.update_user(session=session, user_id=user_id, user_in=user_in)
    if db_user is None:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    return db_user


@router.get("/me/predictions", response_model=List[PredictionOutSchema])
def get_user_preds(session: SessionDep, current_user: CurrentUserDep):
    return get_user_predictions(session=session, user_id=current_user.id)
