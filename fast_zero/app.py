# Importando httpstatus para usar nas resposes
from http import HTTPStatus

# importando FastAPI para inicializar o app, com a HTTPException para tratamentos de exceções
from fastapi import FastAPI, HTTPException
# Importando html do redoc e do swagger para customização
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
# Importando classe HTMLResponse do módulo de responses, para responses em formato de HTML
from fastapi.responses import HTMLResponse
# Importação de schemas
from fast_zero.schema import PublicUser, ReadRoot, UserDB, UserList, UserSchema

# Criação de app para inicializar API
app = FastAPI(title='Cursor - FastAPI', docs_url=None, redoc_url=None)
icon_url = 'https://avatars.githubusercontent.com/u/155389551?s=200&v=4'

# Banco de dados fictício
database: list[UserDB] = []

# Customizando rota de documentação, sem incluir no schema da documentação
@app.get('/docs', include_in_schema=False)
def overridden_swagger():
    # Sobreescrevendo o swagger com título diferente e ícone da página
    return get_swagger_ui_html(
        openapi_url='/openapi.json',
        title='Cursor - FastAP',
        swagger_favicon_url=icon_url,
    )


@app.get('/redoc', include_in_schema=False)
def overridden_redoc():
    # Aplciando mesma lógica do swagger pro redoc
    return get_redoc_html(
        openapi_url='/openapi.json',
        title='Cursor - FastAPI',
        redoc_favicon_url=icon_url,
    )

# Rota padrão, response com status.OK se for sucesso, o modelo de response é o ReadRoot
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

# Rota post para criação de usuários. O retorno de status é diferente,
# é de created. O modelo é diferente, é o schema PublicUser, que remove o password do retorno
@app.post('/user', status_code=HTTPStatus.CREATED, response_model=PublicUser)
def create_user(user: UserSchema):
    # Criando objeto da classe UserDB com as informações passadas no schema do input, o id é dinamico,
    # somando o tamanho do banco de dados + 1
    """user_with_id = UserDB(email=user.email,
        username=user.username, password=user.password,
        id=len(database) + 1)
    Aqui aprendi a importância do kwargs"""
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    # Adiciona na lista (db) o usuário, UserDB criado, mas retorna em formato de publicuser,
    # Sem password
    # o UserDB herda o schema UserSchema, só tem como adicional o campo ID.
    database.append(user_with_id)
    return user_with_id

# Rota para retornar lista de usuários
@app.get('/user', status_code=HTTPStatus.OK, response_model=UserList)
def read_user():
    return {'users': database}

# rota para atualizar registro
@app.put(
    '/user/{userid}', status_code=HTTPStatus.OK, response_model=PublicUser
)
def update_user(userid: int, user: UserSchema):
    # Validação de ID. Se for maior do que o tamanho do banco ou menor que 0, retorna uma exceção HTTP 404
    if userid > len(database) or userid < 0:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    # Localiza o índice e altera por um novo objeto UserDB
    user_with_id = UserDB(**user.model_dump(), id=userid)
    database[userid - 1] = user_with_id

    # Retorna o novo usuário. Com a exibição da senha.
    return user_with_id

# Rota com a mesma lógica de validação da rota de update, porém, deleta.
@app.delete('/user/{userid}', response_model=ReadRoot)
def deleta_user(userid: int):
    if userid > len(database) or userid < 0:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    del database[userid - 1]

    return {'message': 'User deleted'}

# Rota para buscar usuário específico
@app.get('/user/{userid}', response_model=PublicUser)
def get_user_by_id(userid: int) -> UserDB:
    if userid > len(database) or userid <= 0:
        raise HTTPException(
            HTTPStatus.NOT_FOUND, detail='Usuário não encontrado.'
        )

    return database[userid - 1]
