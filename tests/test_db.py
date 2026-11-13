from dataclasses import asdict

from sqlalchemy import select

from fast_zero.models import User

import pytest

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

    user = await sessiontest.scalar(select(User).where(User.username == 'bigmonsa'))

    assert asdict(user) == {
        'id': 1,
        'username': 'bigmonsa',
        'email': 'armandomonsaof@gmail.com',
        'password': 'password123',
        'created_at': time,
        'update_at': time,
    }
