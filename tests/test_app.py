from http import HTTPStatus


def test_api_docs(client, token):
    response = client.get(
        url='/docs', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK


def test_api_redoc(client):
    response = client.get(url='/redoc')

    assert response.status_code == HTTPStatus.OK
