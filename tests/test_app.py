# PAREI EM: Mesmo sem escrever nenhum assert nesse teste, se executarmos os testes, ele falhará

from http import HTTPStatus

from fast_zero.schema import PublicUser


def test_root_should_return_ok_and_hello_world(client):
    # act
    response = client.get('/')

    # assert
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}


def test_root_should_return_html_and_ok(client):
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert 'Hello, World!' in response.text


def test_create_user(client):
    response = client.post(
        '/user',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_read_users(client):
    response = client.get('/user')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_users_with_users(client, user):
    user_schema = PublicUser.model_validate(user).model_dump()
    response = client.get('/user/')
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user):
    response = client.put(
        url=f'/user/{user.id}',
        json={
            'email': 'testuser@gmail.com',
            'username': 'armandomonsaotest',
            'password': 'newpasswordtest',
        },
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': 'testuser@gmail.com',
        'username': 'armandomonsaotest',
    }


def test_update_404_error(client):
    response = client.put(
        url='/user/3',
        json={
            'email': 'testuser@gmail.com',
            'username': 'armandomonsaotest',
            'password': 'newpasswordtest',
        },
    )

    assert response.status_code == HTTPStatus.NOT_FOUND

def test_update_integrity_error(client, user):
    client.post(
        '/user',
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    response_update = client.put(
        f'/user/{user.id}',
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

def test_delete_user(client):
    response = client.delete(url='/user/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_404_error(client):
    response = client.delete(url='/user/3')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}


def test_get_by_id(client):
    response = client.get(url='/user/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'email': 'armando22@gmail.com',
        'username': 'armandomonsao2',
        'id': 2,
    }


def test_get_by_id_404(client):
    response = client.get(url='/user/777')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Usuário não encontrado.'}
