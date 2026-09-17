from http import HTTPStatus

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse

from fast_zero.schema import PublicUser, ReadRoot, UserSchema

app = FastAPI(title='Cursor - FastAPI', docs_url=None, redoc_url=None)
icon_url = 'https://avatars.githubusercontent.com/u/155389551?s=200&v=4'


@app.get('/docs', include_in_schema=False)
def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url='/openapi.json',
        title='Cursor - FastAP',
        swagger_favicon_url=icon_url,
    )


@app.get('/redoc', include_in_schema=False)
def overridden_redoc():
    return get_redoc_html(
        openapi_url='/openapi.json',
        title='Cursor - FastAPI',
        redoc_favicon_url=icon_url,
    )


@app.get('/', status_code=HTTPStatus.OK, response_model=ReadRoot)
def read_root():
    return {'message': 'Hello, World!'}


@app.get('/html', status_code=HTTPStatus.OK, response_class=HTMLResponse)
def read_root_html():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hello, World!</title>
    </head>
    <body>
        <h1>Hello, World!</h1>
    </body>
    </html>
    """


@app.post('/user', status_code=HTTPStatus.CREATED, response_model=PublicUser)
def create_user(user: UserSchema):
    return user
