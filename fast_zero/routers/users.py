from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schema import FilterPage, PublicUser, UserList, UserSchema
from fast_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/user', tags=['Users'])

type SessionDp = Annotated[AsyncSession, Depends(get_session)]
type CurrentUser = Annotated[AsyncSession, Depends(get_current_user)]


@router.get(path='/', status_code=HTTPStatus.OK, response_model=UserList)
async def get_users(
    session: SessionDp, filter_users: Annotated[FilterPage, Query()]
):
    query = await session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    )
    users = query.all()

    return {'users': users}


@router.get(
    path='/{userid}', status_code=HTTPStatus.OK, response_model=PublicUser
)
async def get_user(
    userid: int,
    session: SessionDp,
):
    user = await session.scalar(select(User).where(User.id == userid))

    if user:
        return user
    else:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )


@router.post(
    path='/', status_code=HTTPStatus.CREATED, response_model=PublicUser
)
async def create_user(user: UserSchema, session: SessionDp):
    db_user = await session.scalar(
        select(User).where(
            (User.email == user.email) | (User.username == user.username)
        )
    )

    if db_user and db_user.email == user.email:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Email already exists'
        )
    elif db_user and db_user.username == user.username:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Username already exists'
        )
    else:
        new_user = User(
            username=user.username,
            email=user.email,
            password=get_password_hash(user.password),
        )

        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)

        return new_user


@router.put(
    path='/{userid}', status_code=HTTPStatus.OK, response_model=PublicUser
)
async def update_user(
    userid: int,
    userschema: UserSchema,
    session: SessionDp,
    current_user: CurrentUser,
):
    if userid != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Permission denied'
        )

    try:
        current_user.username = userschema.username
        current_user.email = userschema.email
        current_user.password = get_password_hash(userschema.password)

        await session.commit()
        await session.refresh(current_user)

        return current_user
    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )


@router.delete(path='/{userid}', status_code=HTTPStatus.OK)
async def delete_user(
    userid: int,
    session: SessionDp,
    current_user: CurrentUser,
):

    if userid != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    else:
        await session.delete(current_user)
        await session.commit()

        return {'message': 'User deleted'}
