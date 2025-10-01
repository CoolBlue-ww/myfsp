from uvicorn import Server, Config
from typing import Dict, Any, Optional, List


# class SubConfig(Config):
#     def __init__()

class SubServer(Server):
    def __init__(self, config: Config) -> None:
        super().__init__(config=config)
        self.running = False

    async def serve(self, sockets: Optional[List] = None) -> None:
        self.running = True
        try:
            await super().serve(sockets=sockets)
        finally:
            self.running = False
        return None

class ServerHandler(object):
    __slots__ = ()

    def __init__(self) -> None:
        pass

    def build_server(self, server_args: Dict[str, Any]) -> Server:
        config = Config(
            **server_args
        )
        server = SubServer(config=config)
        return server

__all__ = [
    'SubServer',
    'ServiceHandler',
]

