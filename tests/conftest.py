from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry
from fast_zero.security import create_access_token, get_password_hash

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import factory

class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')

@contextmanager
def _mock_db_time(*, model, time=datetime(2026, 1, 1)):

    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
            target.update_at = time

    # Adiciona um evento, no modelo,
    # antes de inserir, para definir o valor fake do time
    event.listen(model, 'before_insert', fake_time_hook)
    # Retorna o time mockado e aguarda ele terminar de set usado
    yield time
    # Remove o evento do modelo
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def client(sessiontest):
    def get_session_override():
        yield sessiontest

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sessiontest():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest_asyncio.fixture
async def user(sessiontest):
    password = 'testpassword'
    user = UserFactory(password=get_password_hash(password))
    
    sessiontest.add(user)
    await sessiontest.commit()
    await sessiontest.refresh(user)

    setattr(user, 'clean_password', password)

    return user

@pytest_asyncio.fixture
async def other_user(sessiontest):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))

    sessiontest.add(user)
    await sessiontest.commit()
    await sessiontest.refresh(user)

    setattr(user, 'clean_password', password)

    return user

@pytest.fixture
def token(client, user):
    response = client.post(
        'auth/token',
        data={
            'username': user.email,
            'password': getattr(user, 'clean_password'),
        },
    )

    return response.json()['access_token']


@pytest.fixture
def token_without_email():
    return create_access_token(data={'sub': ''})


@pytest.fixture
def token_with_other_email():
    return create_access_token(data={'sub': 'teste22@test.com'})
