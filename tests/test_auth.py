from http import HTTPStatus
from freezegun import freeze_time


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': getattr(user, 'clean_password'),
        },
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token

def test_token_expired_after_time(client, user):
    with freeze_time('2026-11-13 12:00:00'):
        response = client.post(
            '/auth/token',
            data={
                'username': user.email,
                'password': getattr(user, 'clean_password')
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2026-11-13 12:31:00'):
        response = client.put(
            f'/user/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}

# parei em: https://fastapidozero.dunossauro.com/estavel/09/
#tests/test_auth.py::test_token_expired_after_time FAILED