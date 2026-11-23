from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fast_zero.database import get_session
from fast_zero.models import User, Todo
from fast_zero.security import get_current_user
from fast_zero.schema import (
    FilterTodo,
    TodoUpdate,
    TodoList,
    TodoPublic,
    TodoSchema
)
from http import HTTPStatus

router = APIRouter(prefix='/todos', tags=['todos'])

type Session = Annotated[AsyncSession, Depends(get_session)]
type CurrentUser = Annotated[User, Depends(get_current_user)]

@router.post('/', response_model=TodoPublic)
async def create_todo(
    todo: TodoSchema,
    user: CurrentUser,
    session: Session
):
    db_todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id
    )

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo

@router.get('/', response_model=TodoList)
async def list_todos(
    session: Session,
    user: CurrentUser,
    todo_filter: Annotated[FilterTodo, Query()]
):
    query = select(Todo).where(Todo.user_id == user.id)

    if todo_filter.title:
        query = query.filter(Todo.title.contains(todo_filter.title))

    if todo_filter.description:
        query = query.filter(
            Todo.description.contains(todo_filter.description)
        )

    if todo_filter.state:
        query = query.filter(Todo.state.contains(todo_filter.state))

    todos = await session.scalars(
        query.offset(todo_filter.offset).limit(todo_filter.limit)
    )

    return {'todos': todos.all()}

@router.patch('/{todo_id}', response_model=TodoPublic)
async def patch_todo(
    todo_id: int, session: Session, user: CurrentUser,
    todo: TodoUpdate
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found.'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo

# TODO - Entender o uso do @router.patch
# parei em: Para podermos alterar somente os valores que recebemos no modelo