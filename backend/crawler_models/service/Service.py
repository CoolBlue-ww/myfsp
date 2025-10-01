import uvicorn
from pathlib import Path
from typing import Optional, Union, Any, Mapping, List, Tuple, Sequence
import inspect

from fastapi import FastAPI


class Service(object):
    def __init__(self):
        pass
    @staticmethod
    def run(*args, **kwargs) -> None:
        signature = inspect.signature(uvicorn.run)
        bound = signature.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        uvicorn.run(*bound.args, **bound.kwargs)
        return None

service = Service()
service.run(app='Route:app', host="0.0.0.0", port=8000)



