from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schema import Token
from fast_zero.security import (
    create_access_token,
    verify_password,
    get_current_user
)

router = APIRouter(prefix='/auth', tags=['Authentication'])

type SessionDep = Annotated[AsyncSession, Depends(get_session)]
type FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
type Currentuser = Annotated[User, Depends(get_current_user)]

@router.post(path='/token', response_model=Token)
async def create_jwt_token(
    form_data: FormData,
    session: SessionDep,
):
    user = await session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}

@router.post(path='/refresh_token', response_model=Token)
async def refresh_access_token(user: Currentuser):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}