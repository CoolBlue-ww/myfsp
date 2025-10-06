"""
Encapsulate the lifecycle function to automate the management of the app's lifecycle.
Read the app's lifetime in the configuration,
wait asynchronously until the dead time is reached, 
and then send a request to the node to release the shutdown signal.
Simultaneously initialize other independent services.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import Dict, Any
import os, asyncio, httpx
from typing import Union
from monitor import Monitor
import register


TIME = Union[int, float]

async def app_lifespan(
        lifespan: TIME = 10,
        wait: TIME = 0,
) -> None:
    if lifespan > 0:
        await asyncio.sleep(lifespan)
        url = 'http://127.0.0.1:8000/shutdown'
        request_body = {
            'shutdown': True,
            'wait': wait
        }
        headers = {
            'User-Agent': 'MyAPP'
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url,
                json=request_body,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
    else:
        pass  # Always running

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ------------------------------------------------------------
    app.state.server = register.server
    # ------------------------------------------------------------
    shutdown_task = asyncio.create_task(app_lifespan())
    # ------------------------------------------------------------
    monitor = Monitor(
        app=app,
        monitoring_directory='/home/ckr-rocky/桌面/ATC/atc/app/config',
        config_file='',
    )
    observer, monitor_task = await monitor.start_file_monitoring()
    # -------------------------------------------------------------
    yield
    await monitor.stop_file_monitoring(
        observer=observer,
        monitor_task=monitor_task,
    )
    # -------------------------------------------------------------
    try:
        last_response = await shutdown_task
    except Exception:
        pass




