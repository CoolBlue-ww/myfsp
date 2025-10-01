from fastapi import APIRouter
from mitmproxy.options import Options
from mitmproxy.tools.dump import DumpMaster
from typing import Dict, List, Union, TypeVar
from ..config import Config


"""
False
"""
PROXY_ARGUMENTS = {}
ADDONS = {}

proxy_router = APIRouter(
    prefix='/proxy',
    tags=[
        'proxy'
    ]
)

Addons = TypeVar('Addons')

async def _proxy(proxy_arguments: Dict[str, Union[str, int]], addons: Union[List, Addons]) -> None:
    options = Options(
        **proxy_arguments
    )
    master = DumpMaster(options=options)
    master.addons.add(
        addons if isinstance(addons, List) else [addons]
    )
    await master.run()
    return None

@proxy_router.post('/')
async def proxy():
    await _proxy(
        proxy_arguments=PROXY_ARGUMENTS,
        addons=ADDONS,
    )
    message = {
        'message': 'success'
    }
    return message

