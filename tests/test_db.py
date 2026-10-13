from sqlalchemy import select

from dataclasses import asdict

from fast_zero.models import User


def test_create_user(session, mock_db_time):
    # Inicia a função sendo gerenciada dentro de um with, e retorna o valor da data mockada já no time.
    with mock_db_time(model=User) as time:
        # Cria um objeto de User. Nesse momento, o modelo já tem o evento para alterar a data, pois foi passado no parametro model
        new_user = User(
            username='bigmonsa',
            email='armandomonsaof@gmail.com',
            password='password123'
        )
        # Persiste o objeto na sessão
        session.add(new_user)
        # Executa o insert de fato e ativa o evento
        session.commit()

    user = session.scalar(select(User).where(User.username == 'bigmonsa'))

    # Transforma o resultado da consulta acima em dicionário e faz as comparações
    assert asdict(user) == {
        'id': 1,
        'username': 'bigmonsa',
        'email': 'armandomonsaof@gmail.com',
        'password': 'password123',
        'created_at': time,
    }

