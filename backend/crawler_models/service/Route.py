from fastapi import FastAPI, Form
from fastapi.requests import Request
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import asyncio
from pydantic import BaseModel
from typing import Optional, Union
from pathlib import Path
import time
import signal
import os
import redis
from redis import Redis
from selenium import webdriver
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright


def automation(
        tool: str = 'selenium',  # [selenium, playwright]
        browser: str = 'chrome',  # [chrome, edge, firefox]
        enable_async: bool = False,  # [False, True]
):
    """
    配置自动化服务
    :param tool:
    :param browser:
    :param enable_async:
    :return:
    """
    if tool.lower() == 'selenium':
        if browser.lower() == 'chrome':
            driver = webdriver.Chrome()
            return driver
        elif browser.lower() == 'msedge':
            driver = webdriver.Chrome()
            return driver
        elif browser.lower() == 'firefox':
            driver = webdriver.Firefox()
            return driver
        else:
            message = 'The browser "{}" is not supported.'.format(browser)
            raise ValueError(message)

    elif tool.lower() == 'playwright':
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        return page, context, browser, playwright
    else:
        message = 'The tool "{}" is not supported.'.format(tool)
        raise ValueError(message)


def redis_i(*args, **kwargs) -> Redis:
    """
    配置内存共享库服务
    :param args:
    :param kwargs:
    :return:
    """
    share_redis = redis.Redis(*args, **kwargs)
    return share_redis


def proxy():
    """
    配置代理服务
    :return:
    """
    pass


app = FastAPI()

home_dir = Path(__file__).parent.resolve().joinpath('home')
home_html_file = home_dir.joinpath('index').with_suffix('.atc_html')
app.mount('/home', StaticFiles(directory=home_dir, check_dir=True, html=True), name='home')

@app.get('/')
async def redirect_home(request: Request) -> RedirectResponse:
    return RedirectResponse(url='/home', status_code=301)

# @app.get('/home')
# async def home(request: Request) -> FileResponse:
#     """
#     Web Home
#     :param request:
#     :return FileResponse
#     """
#     # home_html_file = Path(__file__).parent.resolve().joinpath('home').with_suffix('.atc_html')
#     return FileResponse(home_html_file)

    # return FileResponse(home_html_file)

class Item(BaseModel):
    shutdown: bool = False
    wait: Optional[Union[int, float]] = None

@app.post('/shutdown')
async def shutdown(item: Item) -> JSONResponse:
    """
    Shutdown
    :param item:
    :return JSONResponse:
    """
    if item.shutdown:
        if item.wait is not None:
            time.sleep(item.wait)
        os.kill(os.getpid(), signal.SIGTERM)
        return JSONResponse({'message': 'Service shutdown successful.'})
    else:
        return JSONResponse({'message': 'Service shutdown failed.'})
