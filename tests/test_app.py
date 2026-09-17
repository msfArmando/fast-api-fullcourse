from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app

client = TestClient(app)


def test_root_should_return_ok_and_hello_world():
    client = TestClient(app)
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}


def test_root_should_return_html_and_ok():
    client = TestClient(app)
    response = client.get('/html')

    assert response.status_code == HTTPStatus.OK
    assert 'Hello, World!' in response.text
