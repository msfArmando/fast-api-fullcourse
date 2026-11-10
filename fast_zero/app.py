# Importando httpstatus para usar nas responses
from http import HTTPStatus

# importando FastAPI para inicializar o app,
#  com a HTTPException para tratamentos de exceções
from fastapi import Depends, FastAPI, HTTPException

# Importando html do redoc e do swagger para customização
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

# Importando class HTMLResponse do módulo de responses,
#  para responses em formato de HTML
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User

# Importação de schemas
from fast_zero.schema import (
    PublicUser,
    ReadRoot,
    Token,
    UserDB,
    UserList,
    UserSchema,
)
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

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


# Rota padrão, response com status.OK se for sucesso,
# o modelo de response é o ReadRoot
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


# USAR NO TRAMPO: SCALAR E DEPENDS


# Rota post para criação de usuários. O retorno de status é diferente,
# é de created. O modelo é diferente, é o schema PublicUser,
#  que remove o password do retorno
@app.post('/user', status_code=HTTPStatus.CREATED, response_model=PublicUser)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user and db_user.username == user.username:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username already exists',
        )
    elif db_user and db_user.email == user.email:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Email already exists',
        )
    else:
        hashed_password = get_password_hash(user.password)

        db_user = User(
            username=user.username, password=hashed_password, email=user.email
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user


# Rota para retornar lista de usuários
@app.get('/user', status_code=HTTPStatus.OK, response_model=UserList)
def read_user(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


# rota para atualizar registro
@app.put(
    '/user/{userid}', status_code=HTTPStatus.OK, response_model=PublicUser
)
def update_user(
    userid: int,
    user: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != userid:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        session.commit()
        session.refresh(current_user)

        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )


@app.delete('/user/{userid}', response_model=ReadRoot)
def deleta_user(
    userid: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != userid:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


# Rota para buscar usuário específico
@app.get('/user/{userid}', response_model=PublicUser)
def get_user_by_id(
    userid: int, session: Session = Depends(get_session)
) -> PublicUser:
    db_user = session.scalar(select(User).where(User.id == userid))

    if db_user:
        return db_user
    else:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )


@app.post('/token', tags=['Authentication'], response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
