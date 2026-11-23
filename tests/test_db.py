from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import User, Todo, TodoState


@pytest.mark.asyncio
async def test_create_user(sessiontest, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(
            username='bigmonsa',
            email='armandomonsaof@gmail.com',
            password='password123',
        )
        sessiontest.add(new_user)
        await sessiontest.commit()

    user = await sessiontest.scalar(
        select(User).where(User.username == 'bigmonsa')
    )

    assert asdict(user) == {
        'id': 1,
        'username': 'bigmonsa',
        'email': 'armandomonsaof@gmail.com',
        'password': 'password123',
        'created_at': time,
        'update_at': time,
        'todos': []
    }

@pytest.mark.asyncio
async def test_create_todo(sessiontest, user):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state=TodoState.draft,
        user_id=user.id
    )

    sessiontest.add(todo)
    await sessiontest.commit()

    todo = await sessiontest.scalar(select(Todo))

    assert asdict(todo) == {
        'description': 'Test Desc',
        'id': 1,
        'state': 'draft',
        'title': 'Test Todo',
        'user_id': 1, 
    }

@pytest.mark.asyncio
async def test_user_todo_relationship(sessiontest, user: User):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )

    sessiontest.add(todo)
    await sessiontest.commit()
    await sessiontest.refresh(user)

    user = await sessiontest.scalar(
        select(User).where(User.id == user.id)
    )

    assert user.todos == [todo]