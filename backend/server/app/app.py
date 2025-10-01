"""
注册各个路由器
"""
from fastapi import FastAPI, Request
from lifespan import lifespan
from routers import (
                    shutdown,
                    )


app = FastAPI(
    title='atc-app',
    lifespan=lifespan,
)

app.include_router(
    shutdown.shutdown_router
)

@app.get('/metrics')
async def metrics():
    return {
        'message': 'success'
    }

@app.get('/')
async def root():
    return {
        'mwssage': "Hello!"
    }

@app.get('/config')
async def get_config(request: Request):
    return request.app.state.config

@app.get('/server')
async def get_server(request: Request):
    if request.app.state.server:
        return {
            'message': 'success',
            'is_alive': request.app.state.server.running
        }

@app.get('/is_alive')
async def is_alive(request: Request):
    server = request.app.state.server
    is_alive = server.running
    return {
        'is_alive': is_alive
    }

