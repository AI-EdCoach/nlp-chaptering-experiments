from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend import crud
from backend.api.v1.dependencies import CurrentUserDep, SessionDep
from backend.core import security
from backend.core.config import settings
from backend.core.security import get_password_hash
from backend.schemas.auth import TokenPayload, Token
from backend.schemas.user import UserCreateSchema, UserReadSchema
from backend.crud import create_user, get_user_by_email
from backend.models import User


router = APIRouter()


@router.post("/login")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


@router.post("/register", response_model=UserReadSchema)
def register(session: SessionDep, user_create_data: UserCreateSchema) -> Any:
    print("registering")
    user: User = get_user_by_email(session=session, email=user_create_data.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    created_user = create_user(session, user_create_data)
    return created_user
