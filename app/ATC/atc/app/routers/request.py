from fastapi import APIRouter
import httpx
import asyncio
from typing import Dict, Any, List

CLIENT_ARGUMENTS = {}
REQUEST_ARGUMENTS = {}
ADDONS = []


request_router = APIRouter(
    prefix='/request',
    tags=['request']
)


async def _request(client_arguments: Dict[str, Any] = {}, request_arguments: Dict[str, Any] = {}):
    async with httpx.AsyncClient(
        **client_arguments
    ) as client:
        method = request_arguments.pop('method', 'get')
        response = await getattr(client, method)(**request_arguments)
        return response


@request_router.post('/')
async def request():
    response = None
    if ADDONS:
        response = await ADDONS
    else:
        response = await _request()
    return response


