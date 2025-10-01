import os, signal, time, asyncio, platform
from typing import Union, Optional
from fastapi import APIRouter, Request, BackgroundTasks
from pydantic import BaseModel
from uvicorn import Server


shutdown_router = APIRouter(
    prefix='/shutdown',
    tags=['shutdown'],
)

async def send_signal(wait: Union[int, float], server: Optional[Server]) -> None:
    await asyncio.sleep(wait)
    system = platform.system().lower()
    try:
        if system == 'windows':
            pid, sig = os.getpid(), signal.CTRL_C_EVENT
            os.kill(pid, sig)
        if system in {'linux', 'macos', 'darwin'}:
            pid, sig = os.getpid(), signal.SIGTERM
            os.kill(pid, sig)
    except Exception:
        server.should_exit = True
    return None

class Item(BaseModel):
    shutdown: bool = False
    wait: Union[int, float] = 0.25

@shutdown_router.get('')
async def shutdown():
    message = {
            'message': '请求方式错误！'
    }
    return message

@shutdown_router.post('')
async def shutdown(item: Item, request: Request):
    shutdown, wait = item.shutdown, item.wait
    server = request.app.state.server
    if shutdown and wait >= 0:
        await send_signal(wait=wait, server=server)   
        message = {
                'message': '关机成功!',
                'timestamp': time.time(),
        }
        return message
    else:
        message = {
            'message': '关机失败！',
            'timestamp': time.time()
        }
        return message
