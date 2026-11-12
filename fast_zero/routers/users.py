from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schema import FilterPage, PublicUser, UserList, UserSchema
from fast_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/user', tags=['Users'])

type SessionDp = Annotated[Session, Depends(get_session)]
type CurrentUser = Annotated[Session, Depends(get_current_user)]


@router.get(path='/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(
    session: SessionDp, filter_users: Annotated[FilterPage, Query()]
):
    users = session.scalars(
        select(User).offset(filter_users.offset).limit(filter_users.limit)
    ).all()

    return {'users': users}


@router.get(
    path='/{userid}', status_code=HTTPStatus.OK, response_model=PublicUser
)
def get_user(
    userid: int,
    session: SessionDp,
):
    user = session.scalar(select(User).where(User.id == userid))

    if user:
        return user
    else:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )


@router.post(
    path='/', status_code=HTTPStatus.CREATED, response_model=PublicUser
)
def create_user(user: UserSchema, session: SessionDp):
    db_user = session.scalar(
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
        session.commit()
        session.refresh(new_user)

        return new_user


@router.put(
    path='/{userid}', status_code=HTTPStatus.OK, response_model=PublicUser
)
def update_user(
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

        session.commit()
        session.refresh(current_user)

        return current_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Internal error: {e}',
        )


@router.delete(path='/{userid}', status_code=HTTPStatus.OK)
def delete_user(
    userid: int,
    session: SessionDp,
    current_user: CurrentUser,
):

    if userid != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    else:
        try:
            session.delete(current_user)
            session.commit()

            return {'message': 'User deleted'}
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail=f'Internal server error: {e}',
            )
