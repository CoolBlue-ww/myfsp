from fastapi import APIRouter, Request, FastAPI
import logging
from launcher import ProxyLauncher

logging.getLogger("mitmproxy").setLevel(logging.CRITICAL)

proxy_router = APIRouter(
    prefix='/proxy',
    tags=['proxy'],
)

proxy_launcher = ProxyLauncher(
    host='127.0.0.1',
    port=8080,
)

@proxy_router.get('/launch')
async def launch_proxy(request: Request):
    await proxy_launcher.launch()
    if proxy_launcher.proxy_task and not proxy_launcher.proxy_task.done():
        return {
            'ProxyLauncher': 'Proxy service successfully started.'
        }
    else:
        return {
            'ProxyLauncher': 'Proxy service unsuccessfully started.'
        }

@proxy_router.get('/land')
async def land_proxy(request: Request):
    await proxy_launcher.land()
    if proxy_launcher.proxy_task and proxy_launcher.proxy_task.done():
        return {
            'ProxyLauncher': 'Proxy service successfully closed.'
        }
    else:
        return {
            'ProxyLauncher': 'Proxy service unsuccessfully closed.'
        }

@proxy_router.get('/running')
async def running_proxy(request: Request):
    running = proxy_launcher.running
    return {'running': running}

@proxy_router.get('/addons')
async def addons_proxy(request: Request):
    _addons = proxy_launcher.addons
    addons = {
        index + 1: str(addon) for index, addon in enumerate(_addons)
    }
    return {
        'addons':addons
    }

@proxy_router.get('/lookup')
async def lookup_proxy(request: Request):
    _lookup = proxy_launcher.lookup
    lookup = {
        k: str(v) for k, v in _lookup.items()
    }
    return {
        'lookup': lookup
    }



app = FastAPI()
app.include_router(proxy_router)

import uvicorn
uvicorn.run(app, host="127.0.0.1", port=8000)