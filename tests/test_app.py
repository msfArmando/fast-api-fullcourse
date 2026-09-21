from http import HTTPStatus


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
        url='/user/',
        json={
            'email': 'armandomonsaof@gmail.com',
            'username': 'armandomonsao',
            'password': 'password123',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'email': 'armandomonsaof@gmail.com',
        'username': 'armandomonsao',
        'id': 1,
    }


def test_read_user(client):
    response = client.get('/user/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {
                'email': 'armandomonsaof@gmail.com',
                'username': 'armandomonsao',
                'id': 1,
            }
        ]
    }


def test_update_user(client):
    response = client.put(
        url='/user/1',
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


def test_delete_user(client):
    response = client.delete(url='/user/1')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}
