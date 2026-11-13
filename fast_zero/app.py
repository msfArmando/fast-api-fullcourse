from http import HTTPStatus

from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

from fast_zero.routers import auth, users
from fast_zero.schema import ReadRoot

app = FastAPI(title='Cursor - FastAPI', docs_url=None, redoc_url=None)

app.include_router(users.router)
app.include_router(auth.router)


@app.get('/docs', include_in_schema=False)
async def overridden_swagger():
    return get_swagger_ui_html(
        openapi_url='/openapi.json',
        title='Cursor - FastAP',
        swagger_favicon_url='https://avatars.githubusercontent.com/u/155389551?s=200&v=4',
    )


@app.get('/redoc', include_in_schema=False)
async def overridden_redoc():
    return get_redoc_html(
        openapi_url='/openapi.json',
        title='Cursor - FastAPI',
        redoc_favicon_url='https://avatars.githubusercontent.com/u/155389551?s=200&v=4',
    )


@app.get('/', status_code=HTTPStatus.OK, response_model=ReadRoot)
async def read_root():  # pragma: no cover
    return {'message': 'Hello, World!'}
