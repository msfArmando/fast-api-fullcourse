from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.database import get_session
from fast_zero.models import User, table_registry


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


@pytest.fixture
def sessiontest():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session():
    conn: Session = get_session()
    yield conn

@pytest.fixture
def user(sessiontest):
    user = User(
        username='Teste', email='teste@test.com', password='testpassword'
    )
    sessiontest.add(user)
    sessiontest.commit()
    sessiontest.refresh(user)

    return user

