from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import HTMLResponse

from fast_zero.schema import PublicUser, ReadRoot, UserDB, UserList, UserSchema

app = FastAPI(title='Cursor - FastAPI', docs_url=None, redoc_url=None)
icon_url = 'https://avatars.githubusercontent.com/u/155389551?s=200&v=4'

database: list[UserDB] = []


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
    """user_with_id = UserDB(email=user.email,
        username=user.username, password=user.password,
        id=len(database) + 1)
    Aqui aprendi a importância do kwargs"""
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)
    return user_with_id


@app.get('/user', status_code=HTTPStatus.OK, response_model=UserList)
def read_user():
    return {'users': database}


@app.put(
    '/user/{userid}', status_code=HTTPStatus.OK, response_model=PublicUser
)
def update_user(userid: int, user: UserSchema):
    if userid > len(database) or userid < 0:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    user_with_id = UserDB(**user.model_dump(), id=userid)
    database[userid - 1] = user_with_id

    return user_with_id


@app.delete('/user/{userid}', response_model=ReadRoot)
def deleta_user(userid: int):
    if userid > len(database) or userid < 0:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    del database[userid - 1]

    return {'message': 'User deleted'}


@app.get('/user/{userid}', response_model=PublicUser)
def get_user_by_id(userid: int) -> UserDB:
    if userid > len(database) or userid <= 0:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    return database[userid - 1]
