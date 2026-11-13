from datetime import datetime
from http import HTTPStatus

from fast_zero.schema import PublicUser


def test_get_by_id(client, user):
    response = client.get(url=f'/user/{user.id}')

    user_schema = PublicUser.model_validate(user).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'email': 'teste@test.com',
        'username': 'Teste',
        'created_at': datetime.strftime(
            user_schema['created_at'], '%Y-%m-%dT%H:%M:%S'
        ),
        'update_at': datetime.strftime(
            user_schema['update_at'], '%Y-%m-%dT%H:%M:%S'
        ),
    }


def test_get_by_id_404(client):
    response = client.get(url='/user/777')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}

def test_create_user(client):
    response = client.post(
        '/user',
        json={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'secret',
        },
    )

    response_api = client.get(url='/user/1')

    response_user = response_api.json()

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'alice',
        'email': 'alice@example.com',
        'id': 1,
        'created_at': response_user['created_at'],
        'update_at': response_user['update_at'],
    }

def test_read_users(client):
    response = client.get('/user')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}

def test_read_users_with_users(client, user):
    user_schema = PublicUser.model_validate(user).model_dump()
    response = client.get('/user/')

    response_api = response.json()

    assert {
        'id': response_api['users'][0]['id'],
        'email': response_api['users'][0]['email'],
        'username': response_api['users'][0]['username'],
        'created_at': response_api['users'][0]['created_at'],
        'update_at': response_api['users'][0]['update_at'],
    } == {
        'id': user_schema['id'],
        'email': user_schema['email'],
        'username': user_schema['username'],
        'created_at': datetime.strftime(
            user_schema['created_at'], '%Y-%m-%dT%H:%M:%S'
        ),
        'update_at': datetime.strftime(
            user_schema['update_at'], '%Y-%m-%dT%H:%M:%S'
        ),
    }


def test_update_user(client, user, token):
    response = client.put(
        url=f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'email': 'testuser@gmail.com',
            'username': 'armandomonsaotest',
            'password': 'newpasswordtest',
        },
    )

    response_api = client.get(url=f'/user/{user.id}')
    response_user = response_api.json()

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'email': 'testuser@gmail.com',
        'username': 'armandomonsaotest',
        'created_at': response_user['created_at'],
        'update_at': response_user['update_at'],
    }


def test_update_403_error(client, token):
    response = client.put(
        url='/user/3',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'email': 'testuser@gmail.com',
            'username': 'armandomonsaotest',
            'password': 'newpasswordtest',
        },
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_post_already_exists_username(client, user):
    response = client.post(
        '/user',
        json={
            'username': user.username,
            'email': 'testedev@testdev.com',
            'password': user.password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_post_already_exists_email(client, user):
    response = client.post(
        '/user',
        json={
            'username': 'Testedev',
            'email': user.email,
            'password': user.password,
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_update_integrity_error(client, user, token):
    client.post(
        '/user',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'fausto@example.com',
            'password': 'secret',
        },
    )

    response_update = client.put(
        f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'fausto',
            'email': 'bob@example.com',
            'password': 'mynewpassword',
        },
    )

    assert response_update.status_code == HTTPStatus.CONFLICT
    assert response_update.json() == {
        'detail': 'Username or Email already exists'
    }


def test_delete_user(client, user, token):
    response = client.delete(
        url=f'/user/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_404_error(client, token):
    response = client.delete(
        url='/user/3', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_token(client, user):
    response = client.post(
        'auth/token',
        data={
            'username': user.email,
            'password': getattr(user, 'clean_password'),
        },
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_get_token_not_user(client, user):
    response = client.post(
        'auth/token',
        data={
            'username': 'email2@gmail.com',
            'password': getattr(user, 'clean_password'),
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_get_token_invalid_password(client, user):
    response = client.post(
        'auth/token',
        data={'username': user.email, 'password': 'invalid-password'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
