import pytest
from contextlib import contextmanager
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from fast_zero.app import app
from fast_zero.models import table_registry

# O context manager serve para usar uma função como with
@contextmanager
# Recebe um modelo, que receberá um evento posteriormente, 
# e define por padrão a data que será definida no atributo created_at
def _mock_db_time(*, model, time=datetime(2026, 1, 1)):

    def fake_time_hook(target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    # Adiciona um evento, no modelo, antes de inserir, para definir o valor fake do time
    event.listen(model, 'before_insert', fake_time_hook)
    # Retorna o time mockado e aguarda ele terminar de ser usado
    yield time
    # Remove o evento do modelo
    event.remove(model, 'before_insert', fake_time_hook)

@pytest.fixture
def mock_db_time():
    return mock_db_time

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)
    engine.dispose()
